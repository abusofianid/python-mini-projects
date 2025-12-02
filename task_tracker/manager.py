from datetime import datetime
import storage
import config

# class untuk mengelola tugas-tugas


class taskmanager:

    # fungsi untuk mendapatkan timestamp saat ini dalam format iso string
    def get_timestamp(self):
        return datetime.now().isoformat()
    # fungsi untuk menambahkan tugas baru

    def add_task(self, description):
        # ambil data dari file
        tasks = storage.load_data()
        # buat id baru, jika list kosong, id=1, jika tidak, id terakhir +1
        new_id = 1 if not tasks else max(t["id"] for t in tasks) + 1
        # susun struktur data tugas baru
        new_task = {
            "id": new_id,
            "description": description,
            "status": config.status_todo,
            "created_at": self.get_timestamp(),
            "updated_at": self.get_timestamp()
        }
        # tambahkan ke list dan simpan ke file
        tasks.append(new_task)
        storage.save_data(tasks)
        # kembalikan id tugas baru
        return new_id

    # fungsi memperbrui deskripsi tugas yang ada
    def update_task(self, task_id, description):
        tasks = storage.load_data()
        for task in tasks:
            if task["id"] == task_id:
                task['description'] = description
                task["updated_at"] = self.get_timestamp()
                storage.save_data(tasks)
                return True
        # gagal id tidak ditemukan
        return False

    # fungsi memperbarui status tugas
    def update_task_status(self, task_id, new_status):
        tasks = storage.load_data()
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = new_status
                task["updated_at"] = self.get_timestamp()
                storage.save_data(tasks)
                return True
        return False
    # fungsi menghapus tugas

    def delete_task(self, task_id):
        tasks = storage.load_data()
        # hitung jumlah tugas dan masukkan ke variabel
        initial_count = len(tasks)
        # buat filtering list tugas, hanya yang id tidak sama dengan task_id
        tasks = [t for t in tasks if t["id"] != task_id]
        # jika jumlah tugas berkurang, berarti ada yang dihapus
        if len(tasks) < initial_count:
            storage.save_data(tasks)
            return True
        return False
    # fungsi melihat semua tugas

    def list_tasks(self, status_filter=None):
        tasks = storage.load_data()
        # jika ada filter status, lakukan filtering
        if status_filter:
            return [t for t in tasks if t["status"] == status_filter]
        return tasks
