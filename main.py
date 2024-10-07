def assign_tasks(factor, arrival, bonus, reward, duration, time_bonus):
    import heapq

    T = len(arrival)  # number of tasks
    P = len(factor[0])  # number of processors

    # Initialize processors
    next_available_time = [0] * P  # For each processor p, when it will be next available
    processors = ['free'] * P  # Processor status: 'free' or 'busy'

    scheduled = [False] * T  # scheduled[i] = True if task i is scheduled
    scheduled_tasks = {}  # task i: (p, t)

    available_tasks = set()  # set of task indices
    free_processors = set(range(P))  # processors that are free

    # Initialize event queue
    # Each event is a tuple (event_time, event_type, event_info)
    # event_type is 'arrival' or 'finish'
    # event_info is task index for 'arrival', processor index for 'finish'
    event_queue = []

    # Add arrival events
    for i in range(T):
        heapq.heappush(event_queue, (arrival[i], 'arrival', i))

    while event_queue or any(not s for s in scheduled):
        if event_queue:
            t, event_type, info = heapq.heappop(event_queue)
        else:
            # If no events left but tasks are unscheduled, advance time to earliest arrival
            unscheduled_tasks = [i for i in range(T) if not scheduled[i]]
            if not unscheduled_tasks:
                break
            next_arrival_time = min(arrival[i] for i in unscheduled_tasks)
            t = next_arrival_time
            event_type = 'arrival'
            info = None

        # Process all events at time t
        events_at_t = [(t, event_type, info)]
        while event_queue and event_queue[0][0] == t:
            events_at_t.append(heapq.heappop(event_queue))

        for event in events_at_t:
            t_event, event_type, info = event
            if event_type == 'arrival':
                # Task arrival
                if info is not None:
                    i = info
                    available_tasks.add(i)
            elif event_type == 'finish':
                # Processor becomes free
                p = info
                processors[p] = 'free'
                free_processors.add(p)
            else:
                continue  # Should not reach here

        # While there are free processors and available tasks, schedule tasks
        while free_processors and available_tasks:
            best_i = None
            best_p = None
            best_R = -1
            t_i = t  # scheduling time

            for i in available_tasks:
                s = t_i - arrival[i]
                D = duration[i]
                s = max(0, s)  # s >= 0
                for p in free_processors:
                    f = factor[i][p]
                    r = reward[i]
                    b = bonus[i]
                    tb = time_bonus[i]

                    if t_i < arrival[i] + tb:
                        # Within bonus time
                        R = f * (b + r * D / (D + s))
                    else:
                        R = f * r * D / (D + s)
                    if R > best_R:
                        best_R = R
                        best_i = i
                        best_p = p

            if best_i is not None:
                # Assign task best_i to processor best_p at time t_i
                scheduled[best_i] = True
                scheduled_tasks[best_i] = (best_p, t_i)
                available_tasks.remove(best_i)
                processors[best_p] = 'busy'
                free_processors.remove(best_p)
                finish_time = t_i + duration[best_i]
                next_available_time[best_p] = finish_time
                # Add finish event
                heapq.heappush(event_queue, (finish_time, 'finish', best_p))
            else:
                break  # No suitable task found

        # If there are no events left and processors are busy, advance time to the next processor finish time
        if not event_queue and any(not s for s in scheduled):
            # Find the earliest next event time
            next_times = []
            if any(not s for s in scheduled):
                unscheduled_arrivals = [arrival[i] for i in range(T) if not scheduled[i]]
                if unscheduled_arrivals:
                    next_times.append(min(unscheduled_arrivals))
            busy_processors = [p for p in range(P) if processors[p] == 'busy']
            if busy_processors:
                next_finish_times = [next_available_time[p] for p in busy_processors]
                next_times.append(min(next_finish_times))
            if next_times:
                next_t = min(next_times)
                # Do nothing and let the loop continue to next event
                continue
            else:
                break  # No more events

    # Prepare the output schedule
    schedule = [None] * T
    for i in range(T):
        if i in scheduled_tasks:
            p, t_i = scheduled_tasks[i]
            schedule[i] = (p, t_i)
        else:
            # In case a task was not scheduled (should not happen), assign it arbitrarily
            schedule[i] = (0, arrival[i])

    return schedule
