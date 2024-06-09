import pygame
from vector2d import Vector2D
from random import uniform, randint
from math import sin, cos, radians

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
        self.alive = True
        
        # Behavior weights
        self.cohesion_weight = 1.0
        self.separation_weight = 1.0
        self.alignment_weight = 1.0
        self.wander_weight = 1.0

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

    def update(self, delta_time): 
        # Calculate the steering force
        steering_force = self.state_machine()
        steering_force.truncate(self.max_force)

        # Apply the force to acceleration
        acceleration = steering_force / self.mass

        # Update velocity and position
        self.velocity += acceleration * delta_time
        self.velocity.truncate(self.max_speed)
        self.position += self.velocity * delta_time

        # Ensure the agent stays within bounds
        self.check_bounds()
        # Check for food collision
        self.check_food_collision()

    def state_machine(self):
        if self.mode == 'carry_food':
            x, y, width, height = self.group.king_zone
            target_pos = Vector2D(x + width / 2, y + height / 2)
            
            # If food already in zone, drop it
            if self.is_in_king_zone():
                self.drop_food()
                self.mode = 'wander'
            return self.seek(target_pos)
        
        elif self.mode == 'wander':
            return self.calculate()
        
    def calculate(self): 
        # Calculate the current steering force
        delta = 3.0
        neighbors = self.get_neighbors(8) # Neighbour detection radius

        cohesion_force = self.cohesion(neighbors) * self.cohesion_weight
        separation_force = self.separation(neighbors) * self.separation_weight
        alignment_force = self.alignment(neighbors) * self.alignment_weight
        
        wander_force = self.wander(delta) * self.wander_weight

        # TEST, flee other faction agents
        enemy = self.detect_enemy()
        if enemy:
            flee_force = self.flee(enemy)
        else:
            flee_force = Vector2D()

        steering_force = cohesion_force + separation_force + alignment_force + wander_force 
        if flee_force != Vector2D():
            steering_force += flee_force
            
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

    def apply_behavior_weights(self, cohesion, separation, alignment, wander):
        self.cohesion_weight = cohesion
        self.separation_weight = separation
        self.alignment_weight = alignment
        self.wander_weight = wander

    def render(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)

    def detect_enemy(self):
        ''' Detect if an enemy is within a radius around the agent '''
        detection_radius = 1.6 * self.scale.x
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

    # Individual steering behaviors
    def wander(self, delta):
        wt = self.wander_target
        jitter_tts = self.wander_jitter * delta
        wt += Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)
        wt.normalise()
        wt *= self.wander_radius
        target = wt + Vector2D(self.wander_distance, 0)
        wld_target = self.world.transform_points([target], self.position, self.velocity.get_normalised(), self.velocity.get_normalised().perp(), self.scale)
        return self.seek(wld_target[0])

    def seek(self, target_pos):
        desired_vel = (target_pos - self.position).normalise() * self.max_speed
        return desired_vel - self.velocity
    
    def flee(self, enemy):
        desired_velocity = (self.position - enemy.position).normalise() * self.max_speed
        return desired_velocity - self.velocity

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

    def is_in_king_zone(self): # Check if agent is in king zone, IMPROVE DROP LOCATION LATER.
        if self.carrying_food:
            x, y, width, height = self.group.king_zone
            margin = 50  # for the inner area
            inner_x = x + margin
            inner_y = y + margin
            inner_width = width - 2 * margin
            inner_height = height - 2 * margin
            return inner_x <= self.position.x <= inner_x + inner_width and inner_y <= self.position.y <= inner_y + inner_height
        return False
    
    
    
    
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
