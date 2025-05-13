import pygame

def main():
    pygame.init()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No joystick connected.")
        return
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    print(f"Joystick name: {joystick.get_name()}")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYHATMOTION:
                if event.value == (0, 1):
                    print("D-pad up")
                elif event.value == (0, -1):
                    print("D-pad down")
                elif event.value == (-1, 0):
                    print("D-pad left")
                elif event.value == (1, 0):
                    print("D-pad right")
                elif event.value == (1,1):
                    print("D-pad up-right")
                elif event.value == (-1,1):
                    print("D-pad up-left")
                elif event.value == (1,-1):
                    print("D-pad down-right")
                elif event.value == (-1,-1):
                    print("D-pad down-left")
            elif event.type == pygame.QUIT:
                return
            

if __name__ == "__main__":
    main()
