from Lib.HifiHelper import HifiHelper
from Lib.MusicApp import MusicApp

import time
from pydub import AudioSegment
from pydub.playback import play


def main():
    app = MusicApp()
    app.init("Hifi Music")
    app.run()
    pass

if __name__ == '__main__':
    main()
