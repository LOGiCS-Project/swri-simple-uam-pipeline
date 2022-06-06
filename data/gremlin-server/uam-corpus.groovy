// Taken From: https://github.com/krlawrence/graph/blob/master/book/Gremlin-Graph-Guide.adoc#servertinkergraph

def globals = [:]

globals << [hook : [
  onStartUp: { ctx ->
    ctx.logger.info("Loading graph data from 'data/all_schema_uam.graphml'.")
    graph.io(graphml()).readGraph('data/all_schema_uam.graphml')
  }
] as LifeCycleHook]

globals << [g : graph.traversal()] // .withStrategies(ReadOnlyStrategy)] 
