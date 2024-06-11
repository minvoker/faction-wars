from game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()




'''
Base world DONE
Agent groups DONE
agent steering DONE

World as searchable graph TO-DO

FSM
- wander: DONE
- carry_food: DONE
- fight: TO-DO

Individual goals
- Bring food: DONE
- Avoid enemy agents / Fight: TO-DO

Faction goals 
- Bring food to king zone: DONE
- Attack other faction: TO-DO
- Explore outward, retreat TO-DO

Environment Objects/objectives TO-DO
- Food DONE
- Walls DONE


Future:
Optimization to allow for more agents
- General code, Grid based (neighbour detection)

'''