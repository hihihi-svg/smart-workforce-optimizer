import heapq

class MinHeap:
    """
    A custom implementation of a Binary Min-Heap.
    Uses an insertion counter as a tie-breaker to prevent comparison errors
    between non-comparable items with the same priority.
    """
    def __init__(self):
        self.heap = []
        self.counter = 0

    def push(self, item, priority):
        """Insert an item with a given priority into the heap."""
        # Entry: (priority, tie_breaker_counter, item)
        entry = (priority, self.counter, item)
        self.counter += 1
        self.heap.append(entry)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        """Remove and return the item with the minimum priority."""
        if self.is_empty():
            raise IndexError("pop from an empty heap")
        
        # Swap root with last element
        self._swap(0, len(self.heap) - 1)
        priority, _, item = self.heap.pop()
        
        if not self.is_empty():
            self._sift_down(0)
            
        return item, priority

    def peek(self):
        """Return the item with the minimum priority without removing it."""
        if self.is_empty():
            raise IndexError("peek from an empty heap")
        priority, _, item = self.heap[0]
        return item, priority

    def is_empty(self):
        """Check if the heap is empty."""
        return len(self.heap) == 0

    def __len__(self):
        """Return the number of elements in the heap."""
        return len(self.heap)

    def _sift_up(self, idx):
        parent_idx = (idx - 1) // 2
        while idx > 0 and self.heap[idx][0] < self.heap[parent_idx][0]:
            self._swap(idx, parent_idx)
            idx = parent_idx
            parent_idx = (idx - 1) // 2

    def _sift_down(self, idx):
        length = len(self.heap)
        while True:
            left_child = 2 * idx + 1
            right_child = 2 * idx + 2
            smallest = idx

            if left_child < length and self.heap[left_child][0] < self.heap[smallest][0]:
                smallest = left_child

            if right_child < length and self.heap[right_child][0] < self.heap[smallest][0]:
                smallest = right_child

            if smallest != idx:
                self._swap(idx, smallest)
                idx = smallest
            else:
                break

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]


class MaxHeap:
    """
    A custom implementation of a Binary Max-Heap.
    Uses an insertion counter as a tie-breaker.
    """
    def __init__(self):
        self.heap = []
        self.counter = 0

    def push(self, item, priority):
        """Insert an item with a given priority into the heap."""
        # Entry: (priority, tie_breaker_counter, item)
        # Note: priority is not negated here, we handle comparison directly in heapify operations
        entry = (priority, self.counter, item)
        self.counter += 1
        self.heap.append(entry)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        """Remove and return the item with the maximum priority."""
        if self.is_empty():
            raise IndexError("pop from an empty heap")
        
        self._swap(0, len(self.heap) - 1)
        priority, _, item = self.heap.pop()
        
        if not self.is_empty():
            self._sift_down(0)
            
        return item, priority

    def peek(self):
        """Return the item with the maximum priority without removing it."""
        if self.is_empty():
            raise IndexError("peek from an empty heap")
        priority, _, item = self.heap[0]
        return item, priority

    def is_empty(self):
        """Check if the heap is empty."""
        return len(self.heap) == 0

    def __len__(self):
        """Return the number of elements in the heap."""
        return len(self.heap)

    def _sift_up(self, idx):
        parent_idx = (idx - 1) // 2
        # Max-Heap checks if current node's priority is greater than parent's
        while idx > 0 and self.heap[idx][0] > self.heap[parent_idx][0]:
            self._swap(idx, parent_idx)
            idx = parent_idx
            parent_idx = (idx - 1) // 2

    def _sift_down(self, idx):
        length = len(self.heap)
        while True:
            left_child = 2 * idx + 1
            right_child = 2 * idx + 2
            largest = idx

            if left_child < length and self.heap[left_child][0] > self.heap[largest][0]:
                largest = left_child

            if right_child < length and self.heap[right_child][0] > self.heap[largest][0]:
                largest = right_child

            if largest != idx:
                self._swap(idx, largest)
                idx = largest
            else:
                break

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

def top_k_candidates(
    employees: list,
    task: dict,
    k: int,
    score_function
) -> list:
    """
    Select the top-K highest scoring employees for a task using a heap.
    Matches the user's specific heap-based selection pattern.
    """
    heap = []

    for emp in employees:
        score = score_function(emp, task)
        if len(heap) < k:
            # We push (score, employee_name)
            heapq.heappush(heap, (score, emp["name"]))
        else:
            if score > heap[0][0]:
                heapq.heapreplace(heap, (score, emp["name"]))

    # Sort the heap in descending order to return top-k in order
    result = sorted(heap, reverse=True)
    return result
