from datetime import datetime
import storage
import config

# class to manage tasks


class taskmanager:

    # function to get the current timestamp as an ISO string
    def get_timestamp(self):
        return datetime.now().isoformat()
    # function to add a new task

    def add_task(self, description):
        # load the data from the file
        tasks = storage.load_data()
        # create a new id: 1 if the list is empty, otherwise the highest id + 1
        new_id = 1 if not tasks else max(t["id"] for t in tasks) + 1
        # build the data structure of the new task
        new_task = {
            "id": new_id,
            "description": description,
            "status": config.status_todo,
            "created_at": self.get_timestamp(),
            "updated_at": self.get_timestamp()
        }
        # add it to the list and save it to the file
        tasks.append(new_task)
        storage.save_data(tasks)
        # return the id of the new task
        return new_id

    # function to update the description of an existing task
    def update_task(self, task_id, description):
        tasks = storage.load_data()
        for task in tasks:
            if task["id"] == task_id:
                task['description'] = description
                task["updated_at"] = self.get_timestamp()
                storage.save_data(tasks)
                return True
        # failed: the id was not found
        return False

    # function to update the status of a task
    def update_task_status(self, task_id, new_status):
        tasks = storage.load_data()
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = new_status
                task["updated_at"] = self.get_timestamp()
                storage.save_data(tasks)
                return True
        return False
    # function to delete a task

    def delete_task(self, task_id):
        tasks = storage.load_data()
        # count the tasks and store the number in a variable
        initial_count = len(tasks)
        # filter the task list, keeping only tasks whose id is not task_id
        tasks = [t for t in tasks if t["id"] != task_id]
        # if the number of tasks decreased, something was deleted
        if len(tasks) < initial_count:
            storage.save_data(tasks)
            return True
        return False
    # function to view all tasks

    def list_tasks(self, status_filter=None):
        tasks = storage.load_data()
        # if there is a status filter, apply it
        if status_filter:
            return [t for t in tasks if t["status"] == status_filter]
        return tasks
