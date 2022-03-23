MATCH (f:Fusion)
WHERE f.name IN ['BCR-ABL', 'BCR-ABL1', 'ABL1-BCR', 'ABL-BCR']
    OR any(name IN f.other_names WHERE name IN ['BCR-ABL', 'BCR-ABL1', 'ABL1-BCR', 'ABL-BCR'] )
WITH collect(f) AS fusions
WHERE size(fusions) > 1
CALL apoc.refactor.mergeNodes(fusions, {properties: 'combine'})
YIELD node
WITH node AS n, node.name AS names, node.other_names AS x
WITH n, head(names) AS name,
CASE
	WHEN size(x) > 0 THEN tail(names) + x
    ELSE tail(names)
END AS other_names
SET n.name = name, n.other_names = other_names
RETURN n