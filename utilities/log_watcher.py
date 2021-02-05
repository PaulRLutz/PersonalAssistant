import time
import os
import sys
import argparse

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "-l", "--level",
      type=int,
      default=0,
      help="The log level to filter by. Defaults to 0."
  )   
  parser.add_argument(
      "-f", "--file",
      default=None,
      help="The file name to filter for."
  )
  parser.add_argument(
      "-u", "--function",
      default=None,
      help="The function name to filter for."
  )

  args = parser.parse_args()
  return args

def main():
  args = get_args()
  log_level = args.level

  log_level_dict = {"CRITICAL" : 50,
                    "ERROR" : 40,
                    "WARNING" : 30,
                    "INFO" : 20,
                    "DEBUG" : 10,
                    "NOTSET" : 0,
                    }

  log_folder = "logs/main"
  current_log_file = get_newest_log_file(log_folder)
  log_timestamp = 0
  current_line = 0
  
  while True:
    if current_log_file is not None:
      if get_file_timestamp(log_folder, current_log_file) > log_timestamp:
        new_lines, current_line, log_timestamp = get_new_lines(log_folder, current_log_file, current_line)
        for line in new_lines:
          log_line = line.strip()
        
          log_line_list = log_line.split("|")
          level_name = log_line_list[0]
          log_time = log_line_list[1]
          file_name = log_line_list[2]
          line_number = log_line_list[3]
          function_name = log_line_list[4]
          log_message = log_line_list[5]


          if log_level_dict[level_name] < log_level:
            continue
          if args.file is not None and args.file != file_name:
            continue
          if args.function is not None and args.function != function_name:
            continue
          log_message_list = log_message.split("<newline>")
        
          log_list = [
              f"{level_name} | {log_time}",
              f"{file_name} | line: {line_number}",
              f"{function_name}()"
              ]
        
          log_list.extend([""] * (len(log_message_list)-len(log_list)))
          log_message_list.extend([""] * (len(log_list)-len(log_message_list)))
        
          final_log_list = zip(log_list, log_message_list)
        
          for log_tuple in final_log_list:
            print("{:<35}".format(log_tuple[0]) + log_tuple[1])
          print("")

    newest_log_file = get_newest_log_file(log_folder)
    if current_log_file != newest_log_file:
      print(f"\n\nSwitching to log file: {newest_log_file}\n\n")
      current_log_file = newest_log_file
      log_timestamp = 0
      current_line = 0
    time.sleep(.25)

def get_new_lines(log_folder, log_file, starting_line):
  new_lines = []
  new_timestamp = get_file_timestamp(log_folder, log_file)
  new_current_line = 0
  with open(f"{log_folder}{os.sep}{log_file}") as log_file:
    for i, line in enumerate(log_file):
      if i >= starting_line:
        new_current_line = i + 1
        new_lines.append(line)
      
  return new_lines, new_current_line, new_timestamp

def get_newest_log_file(log_folder):
  file_names = os.listdir(log_folder)
  
  file_names = [file_name for file_name in file_names if not file_name.endswith(".swp")]

  if len(file_names) <= 0:
    return None, 0

  newest_log_file = file_names[0]
  log_timestamp = get_file_timestamp(log_folder, newest_log_file)

  for file_name in file_names[1:]:
    if get_file_timestamp(log_folder, file_name) > log_timestamp:
      newest_log_file = file_name
      log_timestamp = get_file_timestamp(log_folder, newest_log_file)

  return newest_log_file
  
def get_file_timestamp(log_folder, file_name):
  return os.path.getmtime(f"{log_folder}{os.sep}{file_name}")

if __name__ == "__main__":
  main()
