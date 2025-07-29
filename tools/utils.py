import os
from typing import Union
import requests
import pandas as pd
import subprocess
import sys
from smolagents import tool


@tool
def reverse_string(text: str) -> str:
  """
  Reverse the order of characters in a given string.
  Args:
      text (str): The input string to be reversed.
      
  Returns:
      str: A new string with characters in reverse order.
      
  Example:
      >>> reverse_string("hello")
      'olleh'
      >>> reverse_string("Python")
      'nohtyP'
  """
  return text[::-1]


def download_file(url: str, filename: str) -> str:
  """
  Download a file from the given URL and save it to a temporary location.
  Args:
      url (str): The URL of the file to download.
      filename (str): The name to use for the saved file.
      
  Returns:
      str: Full path to the downloaded file in temporary directory.
      
  Raises:
      requests.RequestException: If the download fails.
      
  Example:
      >>> path = download_file("https://example.com/data.json", "my_data.json")
      >>> print(path)
      '/tmp/tmpxyz123/my_data.json'
  """
    
  file_path = os.path.join("downloaded_files", filename)
  if not os.path.exists(file_path):
      print(f"Attempting to download file from: {url}")
      try:
          response = requests.get(url, timeout=30)
          response.raise_for_status()
          os.makedirs("downloaded_files", exist_ok=True)
          with open(file_path, "wb") as f:
              f.write(response.content)
      except requests.exceptions.RequestException as e:
          print(f"Error downloading file: {e}")
  return file_path

@tool
def process_excel_file(file_path: str) -> pd.DataFrame:
  """
  Process an Excel file and return its data as Pandas DataFrame.
  Args:
    file_path (str): Path to the Excel file (.xlsx or .xls).
   
  Returns:
    pd.DataFrame: processed DataFrame.
  Example:
    >>> result = process_excel_file(
    ...   "data.xlsx",
    ... )
    >>> print(result.head())
  """
  return pd.read_excel(file_path)


@tool
def is_text_file(file_path: str) -> bool:
  """Check if a file is a text file by attempting to decode it as UTF-8.
  Args:
    file_path (str): Path to the file to check.
  Returns:
    bool: True if the file is likely a text file, False if it is likely binary
          or an error occurs.
  Raises:
    None: All exceptions are caught and handled internally.
  Example:
    >>> is_text_file("example.txt")
    True
    >>> is_text_file("image.png")
    False
  """
  try:
    with open(file_path, 'rb') as file:
      # Read a small chunk of the file (1024 bytes)
      chunk: bytes = file.read(1024)
      # Try decoding as UTF-8 text
      chunk.decode('utf-8')
      return True  # No decoding errors, likely a text file
  except UnicodeDecodeError:
    return False  # Decoding failed, likely a binary file
  except Exception as e:
    print(f"Error reading file: {e}")
    return False


@tool
def execute_python_file(file_path: str) -> str:
  """
  Execute a Python code from file_path in a separate process and return its output as a numeric value.
  
  This function runs the specified Python file using the Python interpreter
  in a separate subprocess with error handling and a 60-second timeout.
  
  Args:
      file_path (str): Path to the Python file to execute.
  
  Returns:
      str: The output from the executed script, or an error message if execution failed.
  
  Raises:
      None: All exceptions are handled internally and returned as error strings.
      
  Examples:
      >>> output = execute_python_file("script.py")
      >>> print(output)
      "Hello, World!"
      
      >>> output = execute_python_file("nonexistent.py")
      >>> print(output)
      "Error: File not found: nonexistent.py"
  """
  # Check if file exists
  if not os.path.exists(file_path):
    return f"Error: File not found: {file_path}"
  
  # Check if file is actually a Python file
  if not file_path.endswith('.py'):
    return f"Error: File is not a Python file: {file_path}"
  
  try:
    # Execute the Python file in a separate process
    result = subprocess.run(
      [sys.executable, file_path],
      capture_output=True,
      text=True,
      timeout=180  # 180 seconds timeout
    )
    
    # If there's stderr output, include it in the result
    if result.stderr and result.returncode != 0:
      return f"Error: {result.stderr.strip()}"
    elif result.stderr:
      # Include stderr even if return code is 0 (warnings, etc.)
      return f"{result.stdout.strip()}\nWarnings/Info: {result.stderr.strip()}"
    else:
        for i in result.stdout.strip().split():
          try:
            return str(int(i.strip()))
          except:
            pass
        return result.stdout.strip() if result.stdout.strip() else "Script executed successfully with no output"
    
  except subprocess.TimeoutExpired:
    return "Error: Execution timed out after 60 seconds"
    
  except subprocess.SubprocessError as e:
    return f"Error: Subprocess error: {str(e)}"
    
  except Exception as e:
    return f"Error: Unexpected error: {str(e)}"


@tool
def plural_to_singular(word: str) -> str:
  """
  Convert a plural word to its singular form.
  
  This function handles common English pluralization patterns including:
  - Regular plurals ending in 's' (cats -> cat)
  - Words ending in 'ies' (flies -> fly)
  - Words ending in 'ves' (knives -> knife)
  - Words ending in 'es' after sibilants (boxes -> box)
  - Irregular plurals (children -> child, feet -> foot, etc.)
  
  Args:
    word (str): The plural word to convert to singular form.
    
  Returns:
    str: The singular form of the word.
    
  Examples:
    >>> plural_to_singular("cats")
    'cat'
    >>> plural_to_singular("flies")
    'fly'
    >>> plural_to_singular("children")
    'child'
    >>> plural_to_singular("boxes")
    'box'
  """
  if not word or not isinstance(word, str):
    return word
  
  word = word.lower().strip()
  
  # Handle irregular plurals
  irregular_plurals = {
    'children': 'child',
    'feet': 'foot',
    'teeth': 'tooth',
    'geese': 'goose',
    'mice': 'mouse',
    'men': 'man',
    'women': 'woman',
    'people': 'person',
    'oxen': 'ox',
    'sheep': 'sheep',
    'deer': 'deer',
    'fish': 'fish',
    'species': 'species',
    'series': 'series'
  }
  
  if word in irregular_plurals:
    return irregular_plurals[word]
  
  # Handle words ending in 'ies' -> 'y'
  if word.endswith('ies') and len(word) > 3:
    return word[:-3] + 'y'
  
  # Handle words ending in 'ves' -> 'f' or 'fe'
  if word.endswith('ves'):
    if word[:-3] + 'f' in ['leaf', 'loaf', 'thief', 'shelf', 'knife', 'life', 'wife']:
      return word[:-3] + 'f'
    elif word == 'wolves':
      return 'wolf'
    elif word == 'calves':
      return 'calf'
    elif word == 'halves':
      return 'half'
  
  # Handle words ending in 'es' after sibilants (s, ss, sh, ch, x, z)
  if word.endswith('es') and len(word) > 2:
    if word[-3:-2] in ['s', 'x', 'z'] or word[-4:-2] in ['sh', 'ch', 'ss']:
      return word[:-2]
  
  # Handle words ending in 'oes' -> 'o'
  if word.endswith('oes') and len(word) > 3:
    return word[:-2]
  
  # Handle regular plurals ending in 's'
  if word.endswith('s') and len(word) > 1:
    return word[:-1]
  
  # If no pattern matches, return the original word
  return word
  
@tool
def is_fruit(item: str) -> bool:
  """
  Check if the given item is a recognized fruit.
  
  This function determines whether the provided string matches one of the
  predefined fruits in the internal fruit list. The input is automatically
  converted to singular form and stripped of whitespace before comparison.
  
  The recognized fruits include common varieties such as:
  - Tree fruits: apple, orange, peach, pear, plum, cherry, lemon, lime
  - Berries: strawberry, blueberry, raspberry, grape
  - Tropical fruits: mango, pineapple, kiwi, avocado, pomegranate
  - Dried fruits: fig, date
  - And more: banana
  
  Args:
    item (str): The item name to check against the fruit list. Can be
               singular or plural form.
    
  Returns:
    bool: True if the item is a recognized fruit, False otherwise.
    
  Examples:
    >>> is_fruit("apple")
    True
    >>> is_fruit("apples")
    True
    >>> is_fruit("  Strawberries  ")
    True
    >>> is_fruit("carrot")
    False
    >>> is_fruit("banana")
    True
    
  Note:
    The function uses plural_to_singular() to handle both singular and
    plural forms of fruit names automatically.
  """
  item = plural_to_singular(item.strip())
  fruits = {
    'apple', 'banana', 'orange', 'strawberry', 'blueberry', 'raspberry',
    'mango', 'pineapple', 'grape', 'kiwi', 'peach', 'pear', 'plum',
    'cherry', 'lemon', 'lime', 'avocado', 'pomegranate', 'fig', 'date'
  }
  return item in fruits

@tool
def is_vegetable(item: str) -> bool:
  """
  Check if the given item is a recognized vegetable.
  
  This function determines whether the provided string matches one of the
  predefined vegetables in the internal vegetable list. The input is
  automatically converted to singular form and stripped of whitespace
  before comparison.
  
  The recognized vegetables include various categories:
  - Root vegetables: carrot, onion, garlic, potato, sweet potato
  - Leafy greens: spinach, lettuce, kale, cabbage
  - Cruciferous: broccoli, cauliflower, cabbage, kale
  - Nightshades: tomato, pepper, eggplant
  - Squash family: zucchini
  - Other: cucumber, celery, mushroom
  
  Args:
    item (str): The item name to check against the vegetable list. Can be
               singular or plural form.
    
  Returns:
    bool: True if the item is a recognized vegetable, False otherwise.
    
  Examples:
    >>> is_vegetable("carrot")
    True
    >>> is_vegetable("carrots")
    True
    >>> is_vegetable("  BROCCOLI  ")
    True
    >>> is_vegetable("apple")
    False
    >>> is_vegetable("mushrooms")
    True
    
  Note:
    The function uses plural_to_singular() to handle both singular and
    plural forms of vegetable names automatically. Note that some items
    like tomatoes are botanically fruits but classified as vegetables
    in culinary contexts.
  """
  item = plural_to_singular(item.strip())
  vegetables = {
    'carrot', 'broccoli', 'spinach', 'tomato', 'cucumber', 'lettuce',
    'onion', 'garlic', 'potato', 'sweet potato', 'zucchini', 'pepper',
    'eggplant', 'cauliflower', 'cabbage', 'kale', 'mushroom', 'celery'
  }
  return item in vegetables

@tool
def is_product(item: str) -> bool:
  """
  Check if the given item is a recognized food product or ingredient.
  
  This function determines whether the provided string matches one of the
  predefined food products in the internal product list. The input is
  automatically converted to singular form and stripped of whitespace
  before comparison.
  
  The recognized products include various categories:
  - Baking ingredients: flour, sugar, salt, baking powder, baking soda, yeast
  - Spices and flavorings: pepper, cinnamon, vanilla, honey
  - Dairy products: milk, cream, cheese, yogurt, butter
  - Cooking essentials: oil, vinegar, egg
  - Beverages and treats: juice, ice cream
  - Specialty items: cocoa
  
  Args:
    item (str): The item name to check against the product list. Can be
               singular or plural form.
    
  Returns:
    bool: True if the item is a recognized food product, False otherwise.
    
  Examples:
    >>> is_product("flour")
    True
    >>> is_product("eggs")
    True
    >>> is_product("  Baking Powder  ")
    True
    >>> is_product("carrot")
    False
    >>> is_product("ice cream")
    True
    
  Note:
    The function uses plural_to_singular() to handle both singular and
    plural forms of product names automatically. Some items like 
    "ice cream" are treated as compound terms and matched exactly.
  """
  item = plural_to_singular(item.strip())
  products = {
    'vanilla', 'sugar', 'flour', 'salt', 'pepper', 'oil', 'butter',
    'milk', 'cream', 'cheese', 'yogurt', 'egg', 'honey', 'vinegar',
    'baking powder', 'baking soda', 'yeast', 'cinnamon', 'cocoa', 'juice', 'ice cream'
  }
  return item in products

@tool
def is_food(item: str) -> bool:
  """
  Check if the given item is a recognized food item.
  
  This function determines whether the provided string matches one of the
  predefined food items in the internal food list. The comparison is
  case-insensitive and ignores leading/trailing whitespace.
  
  The recognized food items are:
  - burgers
  - hot dogs
  - salads
  - fries
  - ice cream
  
  Args:
    item (str): The item name to check against the food list.
    
  Returns:
    bool: True if the item is a recognized food item, False otherwise.
    
  Examples:
    >>> is_food("burgers")
    True
    >>> is_food("FRIES")
    True
    >>> is_food("  Ice Cream  ")
    True
    >>> is_food("pizza")
    False
    >>> is_food("books")
    False
    
  Note:
    The function performs case-insensitive matching and automatically
    strips leading and trailing whitespace from the input.
  """  
  return item.lower().strip() in ('burgers', 'hot dogs', 'salads', 'fries', 'ice cream')

@tool
def get_ingredients(item: str) -> str:
  """
  Extract known ingredients from a given text string.
  
  This function identifies and extracts recognized ingredients (fruits, vegetables, 
  and common cooking products) from the input text and returns them as a 
  comma-separated string.
  
  Args:
      item (str): Input text containing potential ingredient names separated by spaces.
  
  Returns:
      str: Comma-separated string of recognized ingredients in alphabetical order.
            Returns empty string if no recognized ingredients are found.
  
  Examples:
      >>> get_ingredients("apple banana flour")
      "apple,banana,flour"
      
      >>> get_ingredients("I need tomato and onion for cooking")
      "onion,tomato"
      
      >>> get_ingredients("car house table")
      ""
      
      >>> get_ingredients("APPLE Carrot SUGAR")
      "apple,carrot,sugar"
  """   

  
  def is_ingredient(ingredient: str) -> bool:
    return is_fruit(ingredient)  or is_vegetable(ingredient) or is_product(ingredient)
  
  items = set([x.lower().strip() for x in item.split() if is_ingredient(x)])
  return ','.join(sorted(items))