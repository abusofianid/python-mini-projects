import os
import shlex  # library agar input dengan tanda kutip dibaca satu kesatuan
from datetime import datetime
from manager import taskmanager
import config


# fungsi utama program
def main():
    manager = taskmanager()
    os.system('cls' if os.name == 'nt' else 'clear')
    # tmapilan cli
    print("="*50)
    print("     Task Tracker CLI")
    print("="*50)
    print("type 'help' for commands list")
    print("type 'exit' to quit the program")
    print("="*50)

    while True:
        try:
            # input user
            user_input = input("task-cli > ").strip()
            # jika user menekan enter tanpa input, ulangi loop
            if not user_input:
                continue
            if user_input.lower() in ["exit"]:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Goodbye!")
                break
            try:
                args = shlex.split(user_input)
            except ValueError:
                print("error:closing quote is missing.")
                continue
            # perintah utama (add, update, delete, list, help)
            command = args[0].lower()
            # argumen tambahan (deskripsi, id, status)
            cmd_args = args[1:]

            # perintah add
            if command == "add":
                if cmd_args:
                    tid = manager.add_task(cmd_args[0])
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"Task added successfully with ID: {tid}")
                else:
                    print("Error: Description is required for adding a task.")
            # perintah update
            elif command == "update":
                # pastikan ada id dan deskripsi
                if len(cmd_args) >= 2:

                    sucess = manager.update_task(int(cmd_args[0]), cmd_args[1])
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(
                        "Task updated successfully." if sucess else "Error: Task ID not found.")
                else:
                    print(
                        "Error: Task ID and new description are required for updating a task.")

            # perintah hapus
            elif command == "delete":
                if cmd_args:
                    sucess = manager.delete_task(int(cmd_args[0]))
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(
                        "Task deleted successfully." if sucess else "Error: Task ID not found.")
                else:
                    print("Error: Task ID is required for deleting a task.")
            # perintah mark status
            elif command == "mark-in-progress":
                if cmd_args:
                    sucess = manager.update_task_status(
                        int(cmd_args[0]), config.status_in_progress)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(
                        "Task marked as In Progress." if sucess else "Error: Task ID not found.")
                else:
                    print(
                        "Error: Task ID is required for marking a task as In Progress.")
            elif command == "mark-done":
                if cmd_args:
                    sucess = manager.update_task_status(
                        int(cmd_args[0]), config.status_done)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(
                        "Task marked as Done." if sucess else "Error: Task ID not found.")
                else:
                    print("Error: Task ID is required for marking a task as Done.")
            # perintah list
            elif command == "list":
                os.system('cls' if os.name == 'nt' else 'clear')
                status = cmd_args[0] if cmd_args else None
                # validasi filter status agar sesuai config
                valid_statuses = [config.status_todo,
                                  config.status_in_progress, config.status_done]
                if status and status not in valid_statuses:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(
                        f"Error: Invalid status filter. Valid options are: {', '.join(valid_statuses)}")
                    continue
                tasks = manager.list_tasks(status)

                if not tasks:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("No tasks found.")
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    # format tampilan tabel
                    print(
                        f"\n{'ID':<5} {'Status':<15} {'Description':<30} {'Created At':<20} {'Updated At':<20}")
                    print("-"*90)
                    # loop mencetak setiap tugas
                    for t in tasks:
                        created = datetime.fromisoformat(
                            t['created_at']).strftime("%d/%m/%Y %H:%M")
                        updated = datetime.fromisoformat(
                            t['updated_at']).strftime("%d/%m/%Y %H:%M")
                        print(
                            f"{t['id']:<5} {t['status']:<15} {t['description']:<30} {created:<20} {updated:<20}")
                    print("")
            elif command == "help":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\nAvailable commands:")
                print(" add \"task description\"             - Add a new task")
                print(
                    " update <task_id> \"new description\" - Update an existing task's description")
                print(" delete <task_id>                   - Delete a task")
                print(" mark-in-progress <task_id>         - Mark a task as In Progress")
                print(" mark-done <task_id>                - Mark a task as Done")
                print(
                    " list [status]                      - List all tasks, optionally filtered by status (todo, in-progress, done)")
                print(" help                               - Show this help message")
                print(" exit                               - Exit the program\n")
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(
                    f"Error: Unknown command '{command}'. Type 'help' for a list of commands.")
        # tangani error konversi id
        except ValueError:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Error: Invalid input. Please check your command and try again.")
        except KeyboardInterrupt:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\nGoodbye!")
            break
        except Exception as e:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
