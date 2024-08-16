// Tumbling window of 1 second
val tumblingWindowStream: WindowedStream[MyEvent, String, TimeWindow] = stream
    .keyBy(event => event.key)
    .window(TumblingProcessingTimeWindows.of(Time.seconds(1)))

// Sliding window of 5 seconds, sliding every 2 seconds
val slidingWindowStream: WindowedStream[MyEvent, String, TimeWindow] = stream
    .keyBy(event => event.key)
    .window(SlidingProcessingTimeWindows.of(Time.seconds(5), Time.seconds(2)))

// Use event time for session windowing
val session_window_event_time = data_stream
    .keyBy(_.key)
    // define the session window with a gap of 10 seconds
    // apply a reduce function to aggregate the events within the session window
    .window(EventTimeSessionWindows.withGap(Time.seconds(10)))
    .reduce((a, b) => Event(a.key, a.value + b.value))

// Use processing time for session windowing
val session_window_processing_time = data_stream
    .keyBy(_.key)
    // define the session window with a gap of 10 seconds
    // apply a reduce function to aggregate the events within the session window
    .window(ProcessingTimeSessionWindows.withGap(Time.seconds(10))) 
    .reduce((a, b) => Event(a.key, a.value + b.value))