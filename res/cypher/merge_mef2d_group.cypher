MATCH (f:Fusion)
WHERE f.name CONTAINS 'MEF2D'
    OR any (n IN f.other_names WHERE n CONTAINS 'MEF2D')
WITH collect(f) AS fusions
WHERE size(fusions) > 1
CALL apoc.refactor.mergeNodes(fusions, {properties: 'combine'})
YIELD node
WITH node AS n, node.name AS names
SET n.name = 'MEF2D group', n.other_names = names
RETURN n