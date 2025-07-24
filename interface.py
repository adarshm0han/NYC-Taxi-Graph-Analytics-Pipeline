from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def _drop_existing_graph(self, session):
        session.run("CALL gds.graph.exists('tripGraph') YIELD exists")
        session.run("CALL gds.graph.drop('tripGraph', false)")  # deprecation warning is OK

    def pagerank(self, max_iterations, weight_property):
        with self._driver.session() as session:
            self._drop_existing_graph(session)

            # Step 1: Project the graph
            session.run(f"""
                CALL gds.graph.project(
                    'tripGraph',
                    'Location',
                    {{
                        TRIP: {{
                            properties: '{weight_property}'
                        }}
                    }}
                )
            """)

            # Step 2: Run PageRank and store results in memory
            session.run(f"""
                CALL gds.pageRank.write('tripGraph', {{
                    maxIterations: $max_iter,
                    dampingFactor: 0.85,
                    relationshipWeightProperty: $weight_prop,
                    writeProperty: 'pagerank_score'
                }})
            """, {
                "max_iter": max_iterations,
                "weight_prop": weight_property
            })

            # Step 3: Return highest and lowest PageRank nodes
            result = session.run("""
                MATCH (n:Location)
                RETURN n.name AS name, n.pagerank_score AS score
                ORDER BY score DESC
                LIMIT 1
                UNION
                MATCH (n:Location)
                RETURN n.name AS name, n.pagerank_score AS score
                ORDER BY score ASC
                LIMIT 1
            """)

            return result.data()

    def bfs(self, start_node, end_node):
        with self._driver.session() as session:
            self._drop_existing_graph(session)

            # Step 1: Project graph without weights
            session.run("""
                CALL gds.graph.project(
                    'tripGraph',
                    'Location',
                    {
                        TRIP: {
                            orientation: 'UNDIRECTED'
                        }
                    }
                )
            """)

            # Step 2: Get internal node ids
            start_result = session.run("MATCH (n:Location {name: $name}) RETURN id(n) AS id", {"name": start_node})
            end_result = session.run("MATCH (n:Location {name: $name}) RETURN id(n) AS id", {"name": end_node})

            start_id = start_result.single()["id"]
            end_id = end_result.single()["id"]

            # Step 3: Run Dijkstra to simulate BFS (since GDS removed shortestPath unweighted)
            result = session.run("""
                CALL gds.shortestPath.dijkstra.stream('tripGraph', {
                    sourceNode: $start_id,
                    targetNode: $end_id
                })
                YIELD nodeIds
                RETURN [nodeId IN nodeIds | gds.util.asNode(nodeId)] AS path
            """, {
                "start_id": start_id,
                "end_id": end_id
            })

            return result.data()
