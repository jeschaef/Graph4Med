MATCH (f:Fusion)
WHERE f.name STARTS WITH 'MLL-' OR f.name ENDS WITH '-MLL' 
    OR any (n IN f.other_names WHERE n STARTS WITH 'MLL-' OR n ENDS WITH '-MLL')
    OR f.name CONTAINS 'KMT2A'
    OR any (n IN f.other_names WHERE n CONTAINS 'KMT2A')
WITH collect(f) AS fusions
WHERE size(fusions) > 1
CALL apoc.refactor.mergeNodes(fusions, {properties: 'combine'})
YIELD node
WITH node AS n, node.name AS names
SET n.name = 'KMT2A group', n.other_names = names
RETURN n