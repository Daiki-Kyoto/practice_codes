import pickle

def deel_file(filename, data=None, save=True):
    if save:
        with open(filename, "wb") as f:
            pickle.dump(data, f)
    else:
        with open(filename, "rb") as f:
            return pickle.load(f)


def phase_change(sender_id, phase):
    deel_file("phase{}.binaryfile".format(sender_id), phase)
