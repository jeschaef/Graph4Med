MATCH (f:Fusion)
WHERE f.name CONTAINS 'ZNF384'
    OR any (n IN f.other_names WHERE n CONTAINS 'ZNF384')
WITH collect(f) AS fusions
WHERE size(fusions) > 1
CALL apoc.refactor.mergeNodes(fusions, {properties: 'combine'})
YIELD node
WITH node AS n, node.name AS names
SET n.name = 'ZNF384 group', n.other_names = names
RETURN n