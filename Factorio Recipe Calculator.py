from os import system, name

current_levels = {
  "assembler": 3,
  "chemical plant": 1,
  "furnace": 1,
  "industrial furnace": 1,
  "oil refinery": 1,
  "fuel refinery": 1,
  "space manufactory": 1,
  "decontamination facility": 1,
  "pulveriser": 1,
  "supercomputer": 1,
  "thermal radiator": 1,
  "biochemical facility": 1,
  "plasma generator": 1,
  "casting machine": 1,
  "centrifuge": 1,
  "mechanical facility": 1,
  "thermodynamics facility": 1
}

crafting_machines = {
  "assembler": [0.5, 0.75, 1.25 * (1 + 4 * 0.3)],  # Assumes 4 spodules
  "chemical plant": [1.9],  # Assumes 3 spodules
  "furnace": [2],
  "industrial furnace": [4 * (1 + .3 * 5)],
  "oil refinery": [1],
  "fuel refinery": [1],
  "pulveriser": [2 * (1 + .3 * 4)],  #4 spodules
  "space manufactory": [10 * (1 + .3 * 6)],  #6 spodules
  "decontamination facility": [2 * (1 + .3 * 4)],  #4 spodulesw
  "supercomputer": [1 * (1 + .3 * 2)],
  "thermal radiator": [1 * (1 + .3 * 2)],
  "biochemical facility": [4 * (1 + .3 * 4)],
  "plasma generator": [1 * (1 + .3 * 4)],
  "casting machine": [1 * (1 + .3 * 2)],
  "centrifuge": [1 * (1 + 0.3 * 2)],
  "mechanical facility": [1 * (1 + .3 * 4)],
  "thermodynamics facility": [4 * (1 + .3 * 4)]
}


def clear():
  if name == 'nt':
    _ = system('cls')
  else:
    _ = system('clear')


def ceil(n):
  if type(n) is float and int(str(n)[:str(n).index(".")]) < n:
    return int(str(n)[:str(n).index(".")]) + 1
  else:
    return int(n)


class Recipe:

  def __init__(self,
               n: int,
               ingredients: list,
               n2: list,
               time=-1,
               crafting_machine="assembler"):
    if len(ingredients) != len(n2):
      raise ValueError("ingredient and ingredient amount must be same length")
    if time == -1:
      raise ValueError("Missing time!")

    self.n = n
    self.ingredients = ingredients
    self.n2 = n2
    if type(n2) is int:
      self.n2 = [n2]
    self.time = time
    self.machine = crafting_machine
    self.crafting_speed = crafting_machines[crafting_machine][
      current_levels[crafting_machine] - 1]

  def get_crafting_machines(self, n: int) -> float:
    return n * self.time / (self.crafting_speed * self.n)

class RecipeBook:

  def __init__(self):
    self.book = {
      "iron gear wheel": Recipe(1, ["iron plate"], [2], 0.2, "assembler"),
      "inserter": Recipe(1, ["small electric motor", "burner inserter"], [1, 1], 0.5,"assembler"),
    }

    self.base_items = [
      "iron plate", "copper plate", "plastic bar", "steel plate", "wood", "stone", "coal"
    ]

  def add_to_base(self, base, item):
    # Helper for combining dictionaries
    for i in range(len(base)):
      if base[i][0] == item[0]:
        base[i][1] += item[1]
    return base

  def get_ingredients(self, itemname, n=1):
    # Check if item is in recipe book
    if itemname in self.book.keys():
      recipe = self.book[itemname]
    else:
      print(f"<{itemname}> is not defined in the recipe book")
      return None
    # Initialize empty crafting machine numbers (in the form- itemname: num_crafters)
    craft = dict()
    # Add original item to crafting list
    craft[itemname] = recipe.get_crafting_machines(n)
    # Intialize empty base items
    base = [[itemname, 0] for itemname in self.base_items]
    # Get initial ingredients and amount needed.
    ingredients = [[recipe.ingredients[i], recipe.n2[i] * n / recipe.n]
                   for i in range(len(recipe.ingredients))]
    # search recipe book
    while len(ingredients) > 0:
      # Items to clear from ingredients after for loop
      to_kill = []
      # Search each ingredient
      for ingredient in ingredients:
        # Check if ingredient is a base ingredient
        if ingredient[0] in self.base_items:
          base = self.add_to_base(base, ingredient)
        # Check if ingredient in recipe book
        elif ingredient[0] in self.book.keys():
          recipe = self.book[ingredient[0]]
          # Add ingredients to crafting list
          if ingredient[0] in craft.keys():
            craft[ingredient[0]] += recipe.get_crafting_machines(ingredient[1])
          else:
            craft[ingredient[0]] = recipe.get_crafting_machines(ingredient[1])
          # Recipe list for ingredient
          new_ingredients = [[
            recipe.ingredients[i], recipe.n2[i] * ingredient[1] / recipe.n
          ] for i in range(len(recipe.ingredients))]
          # Add new ingredients to search list or base items.
          for new_ingredient in new_ingredients:
            if new_ingredient[0] in self.base_items:
              for i in range(len(base)):
                if base[i][0] == new_ingredient[0]:
                  base[i][1] += new_ingredient[1]
            else:
              ingredients.append(new_ingredient)
        # Ingredient is not in recipe nor is a base ingredient.
        else:
          print(f"<{ingredient[0]}> is not defined in the recipe book!")
          return None
        # To remove after for loop
        to_kill.append(ingredient)
      # Remove used ingredients.
      for kill in to_kill:
        ingredients.remove(kill)
    # Print result
    self.display(base, [itemname, n], craft)

  def get_ingredients_dfs(self, itemname, n=1):
    # Similar to get_ingredients, but stores ingredients in a stack rather than a queue.
    if itemname in self.book.keys():
      recipe = self.book[itemname]
    else:
      print(f"<{itemname}> is not defined in the recipe book")
      return None
    craft = [[itemname, recipe.get_crafting_machines(n), 0]]
    base = [[itemname, 0] for itemname in self.base_items]
    ingredients = [[recipe.ingredients[i], recipe.n2[i] * n / recipe.n, 1]
                   for i in range(len(recipe.ingredients))]
    while len(ingredients) > 0:
      ingredient = ingredients[0]
      if ingredient[0] in self.base_items:
        base = self.add_to_base(base, ingredient)
      elif ingredient[0] in self.book.keys():
        recipe = self.book[ingredient[0]]
        craft.append([
          ingredient[0],
          recipe.get_crafting_machines(ingredient[1]), ingredient[2]
        ])
        new_ingredients = [[
          recipe.ingredients[i], recipe.n2[i] * ingredient[1] / recipe.n,
          ingredient[2] + 1
        ] for i in range(len(recipe.ingredients))]
        for new_ingredient in new_ingredients:
          if new_ingredient[0] in self.base_items:
            for i in range(len(base)):
              if base[i][0] == new_ingredient[0]:
                base[i][1] += new_ingredient[1]
          else:
            ingredients = [new_ingredient] + ingredients
      else:
        print(f"<{ingredient[0]}> is not defined in the recipe book!")
        return None
      ingredients.remove(ingredient)
    self.display(base, [itemname, n], craft)

  # Display crafting info
  def display(self, base, info, craft):
    crafters = dict()
    for machine in crafting_machines.keys():
      crafters[machine] = 0
    if base is not None:
      new_str = f"\n{info[0]} x {info[1]} / s:\n"
      for item in base:
        if item[1] != 0:
          new_str += f"    {item[0]}: {round(item[1], 3)}\n"
      craft_str = "\nCrafting Machines:\n"
      if type(craft) is dict:
        for key in craft.keys():
          recipe = self.book[key]
          craft_str += f"    {key}: {ceil(craft[key])} ({recipe.machine} {current_levels[recipe.machine]}) --> {round(recipe.crafting_speed * craft[key] / recipe.time * recipe.n, 1)}/s\n"
        print(new_str + craft_str)
      else:
        for key in craft:
          recipe = self.book[key[0]]
          craft_str += "    " * key[
            2] + f"    {key[0]}: {ceil(key[1])} ({recipe.machine} {current_levels[recipe.machine]}) --> {round(recipe.crafting_speed * key[1] / recipe.time * recipe.n, 1)}/s\n"
          crafters[recipe.machine] += ceil(key[1])
        print(new_str + craft_str)
        print("Total Crafters:")
        for machine in crafters.keys():
          if crafters[machine] > 0:
            print(
              f"    {machine} {current_levels[machine]}: {crafters[machine]}")

if __name__ == "__main__":
  book = RecipeBook()
  flag, skip = True, False
  while flag and not skip:
    itemname = input("Item name?\n").lower()
    if itemname == "q":
      skip = True
    elif itemname in book.book.keys():
      flag = False
    elif itemname in book.base_items:
      print(f"{itemname} is a base item!")
    else:
      print("invalid item name")
  flag = True
  while flag and not skip:
    n = input("How many items per second?\n")
    try:
      float(n)
      flag = False
      n = float(n)
    except ValueError:
      print("Invalid items / s")
  flag = True
  while flag and not skip:
    temp = input(
      "Would you like the crafting machine breakdown? (yes or no)\n").lower()
    if temp in "yes":
      clear()
      book.get_ingredients_dfs(itemname, n)
      flag = False
    elif temp in "no":
      clear()
      book.get_ingredients(itemname, n)
      flag = False
    elif temp in ["both", "b"]:
      clear()
      book.get_ingredients_dfs(itemname, n)
      print("\n===================================")
      book.get_ingredients(itemname, n)
      flag = False
    else:
      print("Invalid answer. (yes or no)")

# TODO:
# Beacon Multiplier Optional Arg