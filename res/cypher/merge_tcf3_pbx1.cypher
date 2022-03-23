MATCH (f:Fusion)
WHERE f.name IN ['TCF3-PBX1', 'PBX1-TCF3', 'E2A-PBX1', 'PBX1-E2A']
    OR any(name IN f.other_names WHERE name IN ['TCF3-PBX1', 'PBX1-TCF3', 'E2A-PBX1', 'PBX1-E2A'])
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