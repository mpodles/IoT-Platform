bridgeName="bridgetest"
userName="mietek"

if __name__ == '__main__':
    print("Your set username is: ",userName)
    yn=input("Do you want to change your name?[y/n]")
    if yn=="y":
       userName= input("Pick new name:\n")
    print("Your bridge name is: ", bridgeName)
    yn = input("Do you want to change your bridge name?[y/n]")
    if yn=="y":
       bridgeName= input("Pick new name:\n")