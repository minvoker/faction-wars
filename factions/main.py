from game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()




'''   MAYBE MAKE KING ZONES IN OPPOSITE CORNERS INSTEAD??? MORE MAP SPACE FOR AGENTS TO WANDER AROUND
Base world DONE
Agent groups DONE
agent steering DONE

FSM - 2 states: wander and carry_food
- wander: DONE
- carry_food: DONE
- fight: TO-DO

Individual goals
- Bring food: DONE
- Avoid enemy agents / Fight: TO-DO

Faction goals 
- Bring food to king zone: DONE
- Attack other faction: TO-DO

Environment Objects/objectives TO-DO
- Food DONE
- Walls TO-DO 


Future:
Optimization to allow for more agents
- General code, Grid based (neighbour detection)

'''