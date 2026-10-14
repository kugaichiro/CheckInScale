class NoteName:
    def __init__(self):
        self.__vecInterval = ["A0","A#0","B0"]
        for i in range(1,8):
            self.__vecInterval.append("C" + str(i))
            self.__vecInterval.append("C#" + str(i))
            self.__vecInterval.append("D" + str(i))
            self.__vecInterval.append("D#" + str(i))
            self.__vecInterval.append("E" + str(i))
            self.__vecInterval.append("F" + str(i))
            self.__vecInterval.append("F#" + str(i))
            self.__vecInterval.append("G" + str(i))
            self.__vecInterval.append("G#" + str(i))
            self.__vecInterval.append("A" + str(i))
            self.__vecInterval.append("A#" + str(i))
            self.__vecInterval.append("B" + str(i))
        self.__vecInterval.append("C8")

    def __iter__(self):
        return iter(self.__vecInterval)

    def index(self, note):
        return self.__vecInterval.index(note)


class NoteNameInOctave:
    def __init__(self):
        self.__vecInterval = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

    def __iter__(self):
        return iter(self.__vecInterval)

    def index(self, note):
        return self.__vecInterval.index(note)

    def get(self, index):
        return self.__vecInterval[index % len(self.__vecInterval)]