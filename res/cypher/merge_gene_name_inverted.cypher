//Merge A-B and B-A
MATCH (a:Fusion), (b:Fusion)
WHERE id(a) < id(b) AND a.name =~ "^\\w+-\\w+"
WITH a, b, split(a.name, '-') AS sa, split(b.name, '-') AS sb
WHERE all(w IN sa WHERE w IN sb)
WITH CASE
    WHEN size(a.name) <= size(b.name) THEN [a,b]
    ELSE [b,a]
    END
AS nodes
CALL apoc.refactor.mergeNodes(nodes, {properties: 'combine'})
YIELD node
WITH node AS n, node.name AS names, node.other_names AS x
WITH n, head(names) AS name,
CASE
	WHEN size(x) > 0 THEN tail(names) + x
    ELSE tail(names)
END AS other_names
SET n.name = name, n.other_names = other_names
RETURN n