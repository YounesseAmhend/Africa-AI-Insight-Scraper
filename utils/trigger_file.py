import logging
import os

class TriggerFile:
    def __init__(self, file_path: str):
        """Initialize TriggerFile with the path to the trigger file.
        
        Args:
            file_path: Path to the trigger file
        """
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Trigger file not found: {self.file_path}")

    def add(self, item: str) -> None:
        """Add a new trigger item to the file.
        
        Args:
            item: The trigger item to add
        """
        with open(self.file_path, 'r+', encoding='utf-8') as f:
            existing_items = {line.strip() for line in f}
            striped_item = item.strip()
            if striped_item not in existing_items:
                f.write(f"{striped_item}\n")

    def remove(self, item: str) -> None:
        """Remove a trigger item from the file.
        
        Args:
            item: The trigger item to remove
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() != item.strip()]

        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")

    def update(self, old_item: str, new_item: str) -> None:
        """Update a trigger item in the file.
        
        Args:
            old_item: The trigger item to update
            new_item: The new trigger item value
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = [
                        new_item.strip() if line.strip() == old_item.strip() else line.strip() 
                        for line in f 
                        if line.strip() # will continue if the line is empty
                    ]

        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")

    def get(self) -> list[str]:
        """Get all trigger items from the file.
        
        Returns:
            List of trigger items
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = [
                line.strip()
                for line in f
                if line.strip() # will skip if the line is empty
            ]
            expected_len = len(set(data))
            data_len = len(data)
            
            if data_len != expected_len:
                logging.warning(
                    f"Trigger file({self.file_path}) contains duplicates - found {data_len - expected_len} duplicate entries."
                )
                data = list(set(data))
            return data
