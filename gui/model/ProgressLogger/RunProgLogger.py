from gui.model.ProgressLogger.TimeLogger import TimeLogger


class RunProgLogger(TimeLogger):
    def write(self, log_entry):
        try:
            remaining = log_entry.split('<')[-1].split(',')[0].split(':')[::1]
            elapsed = log_entry.split('<')[0].split('[')[1].split(':')[::1]
            self.add_to_stack('elapsed: {}m {}s, remaining: {}m {}s'.format(int(elapsed[0]), int(elapsed[1]),
                                                                            int(remaining[0]), int(remaining[1])))
        except Exception:
            pass
