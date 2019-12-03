bridgeName="bridgetest"
userName="mietek"

def replaceBridgeName(newName):
    with open("Setup.py","r") as fr:
        with open("Setup.py", "a") as fw:
            a=fr.readline()
            print(a)


def replaceUserName(newName):
    with open("Setup.py", "r") as fr:
        with open("Setup.py", "a") as fw:
            a = fr.readline(1)
            print(a)


if __name__ == '__main__':
    replaceUserName("dzidza2")
    replaceBridgeName("dzidza")
    print("Your set username is: ",userName)
    yn=input("Do you want to change your name?[y/n]")
    if yn=="y":
        userName= input("Pick new name:\n")
        replaceUserName(userName)
    print("Your bridge name is: ", bridgeName)
    yn = input("Do you want to change your bridge name?[y/n]")
    if yn=="y":
        bridgeName= input("Pick new name:\n")
        replaceBridgeName(bridgeName)