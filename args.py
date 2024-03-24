
import sys


class Args:
    playback: str | None = None
    speed_test: bool = False

    def __init__(self):
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if not arg.startswith('--'):
                raise Exception(f'invalid argument: {arg}')
            if arg == '--playback':
                if i == len(sys.argv) - 1:
                    raise Exception('missing argument for --playback')
                i += 1
                self.playback = sys.argv[i]
            elif arg.startswith('--playback='):
                self.playback = arg[11:]
            elif arg == '--speed-test':
                self.speed_test = True
            else:
                raise Exception(f'uknown argument: {arg}')
            i += 1

    def __str__(self) -> str:
        args = []
        if self.playback is not None:
            args.append(f'--playback={self.playback}')
        if self.speed_test:
            args.append('--speed-test')
        return ' '.join(args)
