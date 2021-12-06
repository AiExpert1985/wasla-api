from datetime import datetime


def expiry_message():
    return ' Your permission is expired \nPlease contact the developer at 07701791983 '


def is_valid():
    return is_valid_counter() and is_valid_date()


def is_valid_date():
    current_date = datetime.now()
    expiry_date = datetime.strptime("1/1/2022 4:00", "%d/%m/%Y %H:%M")
    return expiry_date > current_date


def is_valid_counter():
    counter = 0
    try:
        f = open('smart_gui.txt')
        lines = f.readlines()
        idx1 = lines[2].index('<') + 1
        idx2 = lines[2].index('>')
        counter = int(lines[2][idx1:idx2])
        counter -= 1
        lines[2] = f"<{counter}>"
        f = open('smart_gui.txt', 'w')
        new_lines = ""
        for line in lines:
            new_lines += line
        f.write(new_lines)
        f.close()
    except Exception as e:
        print("error during reading/writing smart_gui file")
        print(e)
    finally:
        return counter > 0
