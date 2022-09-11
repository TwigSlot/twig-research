MATCH (p:Site)
WHERE p.title = 'Strong interaction'
WITH p LIMIT 1
MATCH (p2:Site) WHERE p2.title = p.title AND id(p)<id(p2)
WITH collect(p2) as ps, p
CALL apoc.refactor.mergeNodes(ps) YIELD node
RETURN node


MATCH (p:Site),(p2:Site)
WHERE p.title = p2.title AND id(p)<id(p2)
RETURN p,p2
LIMIT 1000


MATCH (p:Site),(q:Site)
WHERE p.title = q.title AND id(p) < id(q)
WITH p,q LIMIT 1
MATCH (r:Site)
WHERE p.title = r.title
WITH count(r) AS cnt, [p]+collect(r) AS rs, r.title AS title
CALL apoc.refactor.mergeNodes(rs) YIELD node
RETURN cnt, title