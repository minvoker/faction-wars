import pygame
from vector2d import Vector2D
from random import uniform, randint

class Agent:
    def __init__(self, world, position, group, radius=5, color=(255, 0, 0), scale=1, mass=0.8, mode='wander'):
        self.world = world
        self.mode = mode
        self.group = group
        self.position = position
        self.velocity = Vector2D(uniform(-1, 1), uniform(-1, 1))
        self.radius = radius
        self.color = color
        self.scale = Vector2D(scale, scale)
        self.mass = mass
        self.health = 9
        self.alive = True

        # Behavior weights
        self.cohesion_weight = 1.0
        self.separation_weight = 1.0
        self.alignment_weight = 1.0
        self.wander_weight = 1.0
        self.neighbors = []
        
        # Initialize wander properties
        self.wander_target = Vector2D(1, 0)
        self.wander_distance = 1.2 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 2.0 * scale

        # Limits
        self.max_speed = 10.0 * scale
        self.max_force = 500.0

        # Goals
        self.carrying_food = None
        self.target = None
        self.enemy = None
        self.path = []
        self.flocking = False # Test

    def update(self, delta_time):
        # Calculate the steering force
        neighbors = self.get_neighbors(10)  # Neighbour detection radius

        steering_force = self.state_machine(neighbors)
        if steering_force is None:
            steering_force = Vector2D(0, 0)
        steering_force.truncate(self.max_force)

        # Apply the force to acceleration
        acceleration = steering_force / self.mass

        # Update velocity and position
        self.velocity += acceleration * delta_time
        self.velocity.truncate(self.max_speed)
        self.position += self.velocity * delta_time

        # Ensure the agent stays within bounds
        self.check_bounds()
        self.check_wall_collision()
        # Check for food collision
        self.check_food_collision()

    def state_machine(self, neighbors):
        if not self.alive:
            return Vector2D(0, 0)

        if self.mode == 'carry_food':
            x, y, width, height = self.group.king_zone
            self.target = Vector2D(x + width / 2, y + height / 2)

            # If food already in zone, drop it
            if self.is_in_king_zone():
                self.drop_food()
                self.mode = 'wander'
                self.target = None
            # If still holding food
            return self.pathfinder(self.target)

        elif self.mode == 'follow_path':
            force = self.pathfinder(self.target)
            if force is None or (force.x == 0 and force.y == 0):  # Empty Vec2D
                self.mode = 'wander'
            return force

        elif self.mode == 'fight':
            if not self.enemy or not self.enemy.alive:
                self.mode = 'wander'
                return Vector2D(0, 0)

            if self.position.distance(self.enemy.position) < self.radius * 5:
                self.attack_agent(self.enemy)
                return Vector2D(0, 0)
            else:
                print("Chasing", self.enemy.position)
                return self.seek(self.enemy.position)

        elif self.mode == 'wander':
            self.target = None
            if len(neighbors) >= 1 and not self.is_in_king_zone():
                enemy = self.detect_enemy()
                if enemy:
                    print("detected enemy")
                    self.mode = 'fight'
                    self.enemy = enemy
                    self.notify_allies_to_attack(enemy)
            return self.calculate(neighbors)

        return Vector2D(0, 0)  # Default return value to ensure state_machine never returns None

    def calculate(self, neighbors):
        # Calculate the current steering force
        delta = 5.0

        cohesion_force = self.cohesion(neighbors) * self.cohesion_weight
        separation_force = self.separation(neighbors) * self.separation_weight
        alignment_force = self.alignment(neighbors) * self.alignment_weight
        
        if self.flocking:
            self.wander_weight = 0.0
        else:
            self.wander_weight = 0.8
        wander_force = self.wander(delta) * self.wander_weight

        steering_force = cohesion_force + separation_force + alignment_force + wander_force

        steering_force.truncate(self.max_force)

        return steering_force

    def check_bounds(self):
        if self.position.x - self.radius < 0:
            self.position.x = self.radius
            self.velocity.x *= -1
        elif self.position.x + self.radius > self.world.width:
            self.position.x = self.world.width - self.radius
            self.velocity.x *= -1

        if self.position.y - self.radius < 0:
            self.position.y = self.radius
            self.velocity.y *= -1
        elif self.position.y + self.radius > self.world.height:
            self.position.y = self.world.height - self.radius
            self.velocity.y *= -1

    def check_wall_collision(self):
        for wall in self.world.walls:
            if self.inside_wall(wall.rect):
                if self.position.x < wall.rect.left:
                    self.position.x = wall.rect.left - self.radius
                    self.velocity.x *= -1
                elif self.position.x > wall.rect.right:
                    self.position.x = wall.rect.right + self.radius
                    self.velocity.x *= -1

                if self.position.y < wall.rect.top:
                    self.position.y = wall.rect.top - self.radius
                    self.velocity.y *= -1
                elif self.position.y > wall.rect.bottom:
                    self.position.y = wall.rect.bottom + self.radius
                    self.velocity.y *= -1

    def inside_wall(self, rect):
        # Check if the circle (agent) collides with the rectangle (wall)
        closest_x = max(rect.left, min(self.position.x, rect.right))
        closest_y = max(rect.top, min(self.position.y, rect.bottom))
        distance_x = self.position.x - closest_x
        distance_y = self.position.y - closest_y
        distance_squared = (distance_x * distance_x) + (distance_y * distance_y)
        return distance_squared < (self.radius * self.radius)

    def apply_behavior_weights(self, cohesion, separation, alignment, wander):
        self.cohesion_weight = cohesion
        self.separation_weight = separation
        self.alignment_weight = alignment
        self.wander_weight = wander

    def render(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)

    def detect_enemy(self):
        ''' Detect if an enemy is within a radius around the agent '''
        detection_radius = 3 * self.scale.x
        for enemy in self.world.get_other_group_agents(self.group):
            if enemy and enemy != self:
                distance_to_enemy = (enemy.position - self.position).length()
                if distance_to_enemy < detection_radius:
                    return enemy
        return None

    def get_neighbors(self, radius):
        neighbors = []
        for agent in self.group.get_agents():
            if agent != self and self.position.distance(agent.position) <= radius:
                neighbors.append(agent)
        return neighbors

    # Group steering behaviors
    def calculate_average_heading(self, neighbors):
        if not neighbors:
            return Vector2D()

        sum_heading = Vector2D()
        for agent in neighbors:
            sum_heading += agent.velocity.get_normalised()

        return sum_heading / len(neighbors)

    def calculate_center_position(self, neighbors):
        if not neighbors:
            return Vector2D()
        sum_pos = Vector2D()

        for agent in neighbors:
            sum_pos += agent.position

        return sum_pos / len(neighbors)

    def cohesion(self, neighbors):
        if not neighbors:
            return Vector2D()

        center_of_mass = self.calculate_center_position(neighbors)
        desired_velocity = (center_of_mass - self.position).normalise() * self.max_speed

        return desired_velocity - self.velocity

    def separation(self, neighbors):
        if not neighbors:
            return Vector2D()

        separation_force = Vector2D()
        for agent in neighbors:
            direction = self.position - agent.position
            distance = direction.length()

            if distance > 0:
                separation_force += direction.normalise() * (1.0 / distance)

        return separation_force

    def alignment(self, neighbors):
        if not neighbors:
            return Vector2D()

        average_heading = self.calculate_average_heading(neighbors)
        return average_heading - self.velocity.get_normalised()

    def start_flocking(self):
        self.flocking = True
        self.apply_behavior_weights(0.8, 0.8, 0.7, 0.4) # Increase cohesion
        
    def stop_flocking(self):
        self.flocking = False
        self.apply_behavior_weights(0.4, 0.4, 0.4, 0.4) # Reset to 0.4
        
    # Individual steering behaviors
    def wander(self, delta):  # For random wandering
        wt = self.wander_target
        jitter_tts = self.wander_jitter * delta
        wt += Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)
        wt.normalise()
        wt *= self.wander_radius
        target = wt + Vector2D(self.wander_distance, 0)
        wld_target = self.world.transform_points([target], self.position, self.velocity.get_normalised(), self.velocity.get_normalised().perp(), self.scale)
        return self.seek(wld_target[0])

    def seek(self, target_pos):  # Use for targeting enemies
        desired_vel = (target_pos - self.position).normalise() * self.max_speed
        return desired_vel - self.velocity

    def flee(self, enemy):  # Not implemented yet
        desired_velocity = (self.position - enemy.position).normalise() * self.max_speed
        return desired_velocity - self.velocity

    def pathfinder(self, target):  # For exploring, seems to work for now
        if not self.path:
            self.path = self.world.plan_path(self.position, target)  # Use A* to plan path
            if not self.path:  # If no path is found, return an empty vector
                print("DEBUG: NO PATH FOUND")
                return self.seek(target)

        if self.path:
            next_pos = self.path[0]
            if self.position.distance(next_pos) < self.radius:
                self.path.pop(0)
                if not self.path:  # Path is completed
                    return Vector2D(0, 0)
            return self.seek(next_pos)

        print("DEBUG: PATHFINDER CALLED WITH NO PATH")
        return Vector2D(0, 0)

    # Goals and objectives --------------------------------------------------------------------------------------------------
    # FOOD
    def drop_food(self):
        if self.carrying_food:
            self.carrying_food.being_held_by = None
            self.carrying_food = None
            self.mode = 'wander'
            

    def check_food_collision(self):
        if self.carrying_food is None:
            for food in self.world.food:
                if self.position.distance(food.position) < self.radius + food.radius and not food.is_in_king_zone(self.group):
                    if food.being_held_by is None:
                        food.add_touching_agent(self)
                        self.carrying_food = food
                        food.being_held_by = self
                        self.mode = 'carry_food'
                        break

    def is_in_king_zone(self):  # Check if agent is in king zone, IMPROVE DROP LOCATION LATER.
        x, y, width, height = self.group.king_zone
        margin = 50  # for the inner area
        inner_x = x + margin
        inner_y = y + margin
        inner_width = width - 2 * margin
        inner_height = height - 2 * margin
        return inner_x <= self.position.x <= inner_x + inner_width and inner_y <= self.position.y <= inner_y + inner_height 

    # Attack
    def notify_allies_to_attack(self, enemy):
        # Notify nearby allies to attack the detected enemy
        for agent in self.neighbors:
            if agent.group == self.group:
                agent.enemy = enemy # #
                agent.mode = 'fight'
                print("Now Chasing", agent.enemy.position)
                agent.seek(enemy.position)
                

    def attack_agent(self, enemy):
        print("Attacking")
        if self.position.distance(enemy.position) < self.radius * 3:
            enemy.health -= 3
            print(f"Enemy health: {enemy.health}")
            if enemy.health <= 0:
                enemy.alive = False
                self.enemy = None
                print("Enemy killed")

class KingAgent(Agent):
    def __init__(self, world, position, group, zone, radius=10, color=(0, 255, 0), scale=0.7, mass=1):
        super().__init__(world, position, group, radius, color, scale, mass)
        self.zone = zone  # tuple: (x, y, width, height)

    def check_bounds(self):
        x, y, width, height = self.zone

        if self.position.x < x + self.radius:
            self.position.x = x + self.radius
            self.velocity.x = abs(self.velocity.x)
        elif self.position.x > x + width - self.radius:
            self.position.x = x + width - self.radius
            self.velocity.x = -abs(self.velocity.x)

        if self.position.y - self.radius < y:
            self.position.y = y + self.radius
            self.velocity.y *= -1
        elif self.position.y + self.radius > y + height:
            self.position.y = y + height - self.radius
            self.velocity.y *= -1
