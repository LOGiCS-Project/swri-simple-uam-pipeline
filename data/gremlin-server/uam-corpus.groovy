// Taken From: https://github.com/krlawrence/graph/blob/master/book/Gremlin-Graph-Guide.adoc#servertinkergraph

def globals = [:]

globals << [hook : [
  onStartUp: { ctx ->
    ctx.logger.info("Loading graph data from '<<CORPUS_DATA>>'.")
    graph.io(graphml()).readGraph('<<CORPUS_DATA>>')
  }
] as LifeCycleHook]

globals << [g : graph.traversal().withStrategies(<<TRAVERSAL_STRATEGIES>>)]
