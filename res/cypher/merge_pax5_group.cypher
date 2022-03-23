MATCH (f:Fusion)
WHERE f.name CONTAINS 'PAX5'
    OR any (n IN f.other_names WHERE n CONTAINS 'PAX5')
WITH collect(f) AS fusions
WHERE size(fusions) > 1
CALL apoc.refactor.mergeNodes(fusions, {properties: 'combine'})
YIELD node
WITH node AS n, node.name AS names
SET n.name = 'PAX5 group', n.other_names = names
RETURN n