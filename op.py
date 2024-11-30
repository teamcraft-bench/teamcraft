from teamcraft import BuildEnv as Env
import time
import argparse



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Script to evaluate a checkpoint")

  parser.add_argument("--duration", type=int, default=100, help="Duration to wait for user to join the server")
  parser.add_argument("--mc_port", type=int, default=2037, help="Minecraft server port")
  parser.add_argument("--username", type=str, help="Minecraft username, case sensitive")
  
  args = parser.parse_args()
    
  env = Env(mc_port = args.mc_port)
  print("\n------Server is running------\n")
  print(f"Please join MC server now within {args.duration} seconds. \nIf you need to change the duration, please start op.py with 'python op.py --duration YOUR_DURATION_HERE'.")

  # login to Minecraft server within the program halt time.
  time.sleep(args.duration)
  
  print()
  env.mc_server_thread.send_command(f"/op {args.username}") # Case sensitive
  print(f"User {args.username} has been granted OP permission. You should see prompt in game indicate you have became OP")
  print()

  print("Server will be closed in 30 seconds.")
  time.sleep(30)
  
  # clone env
  env.close()