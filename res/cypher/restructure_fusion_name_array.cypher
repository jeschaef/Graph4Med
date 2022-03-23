MATCH (a:Fusion)
UNWIND a.name AS names          // UNWIND + count(names) to distinguish String[] and String without apoc.meta.cypher.isType()
WITH a, count(names) AS num
WHERE num > 1
WITH a, a.name AS names, a.other_names AS x
WITH a, head(names) AS name,
CASE
	WHEN size(x) > 0 THEN tail(names) + x
    ELSE tail(names)
END AS other_names
SET a.name = name, a.other_names = other_names
RETURN a