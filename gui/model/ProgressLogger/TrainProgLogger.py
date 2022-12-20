from gui.model.ProgressLogger.TimeLogger import TimeLogger


class TrainProgLogger(TimeLogger):
    def write(self, log_entry):
        record = str(log_entry)
        tokens = record.split(":")
        if len(tokens) > 1:
            rem = tokens[3].replace("remaining", "").strip()
            tot = tokens[4].strip()

            # tot_min = parse("{:g}m", tot)
            # tot_sec = parse("{:g}s", tot)
            # tot_ms = parse("{:g}ms", tot)
            # tot_us = parse("{:g}us", tot)
            #
            # rem_min = parse("{:g}m", rem)
            # rem_sec = parse("{:g}s", rem)
            # rem_ms = parse("{:g}ms", rem)
            # rem_us = parse("{:g}us", rem)
            #
            # obj = {
            #     'min': _validate_value(rem_min),
            #     'sec': _validate_value(rem_sec),
            #     'ms': _validate_value(rem_ms),
            #     'us': _validate_value(rem_us)
            # }
            self.add_to_stack('elapsed: {}, remaining: {}'.format(rem, tot))
