MATCH (f:Fusion)
WHERE f.name IN ['ETV6-RUNX1', 'RUNX1-ETV6','TEL-AML1', 'AML1-TEL']
    OR any(name IN f.other_names WHERE name IN ['ETV6-RUNX1', 'RUNX1-ETV6','TEL-AML1', 'AML1-TEL'])
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