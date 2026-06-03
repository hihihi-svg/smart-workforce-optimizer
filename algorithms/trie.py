class TrieNode:
    """A node in the Trie prefix tree."""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.original_words = set()  # Set of original-case words matching this path
        self.data_list = []          # List of data objects associated with this word

class Trie:
    """
    A custom Trie (Prefix Tree) implementation.
    Supports case-insensitive autocomplete search, prefix matching,
    and storing metadata at word endpoints.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, data=None):
        """
        Insert a word into the Trie with optional associated data.
        Searches and keys are treated case-insensitively.
        """
        if not word:
            return

        cleaned_word = word.strip().lower()
        node = self.root
        
        for char in cleaned_word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            
        node.is_end_of_word = True
        node.original_words.add(word.strip())
        if data is not None:
            # Avoid inserting duplicate references of data if already present
            if data not in node.data_list:
                node.data_list.append(data)

    def search(self, word: str) -> list:
        """
        Search for an exact match of a word (case-insensitively).
        Returns the list of associated data or an empty list if not found.
        """
        if not word:
            return []

        cleaned_word = word.strip().lower()
        node = self._find_node(cleaned_word)
        
        if node and node.is_end_of_word:
            return node.data_list
        return []

    def starts_with(self, prefix: str) -> list:
        """
        Find all words in the Trie that start with the given prefix.
        Returns a list of dictionaries with structure:
            {"word": original_case_word, "data": data_list}
        """
        if not prefix:
            return []

        cleaned_prefix = prefix.strip().lower()
        node = self._find_node(cleaned_prefix)
        if not node:
            return []

        results = []
        # Run DFS to find all completions from this node
        self._dfs(node, results)
        return results

    def _find_node(self, sequence: str) -> TrieNode:
        """Traverse the Trie to find the node corresponding to sequence."""
        node = self.root
        for char in sequence:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _dfs(self, node: TrieNode, results: list):
        """Depth-first search helper to find all endpoints and retrieve data."""
        if node.is_end_of_word:
            for orig_word in node.original_words:
                results.append({
                    "word": orig_word,
                    "data": node.data_list
                })
        
        # Recursively search children (sorted keys to maintain alphabet order)
        for char in sorted(node.children.keys()):
            self._dfs(node.children[char], results)

    def search_prefix(self, prefix: str) -> list:
        """
        Find all data values associated with keys starting with prefix.
        Returns a flat list of unique values (e.g. employee names).
        """
        results = self.starts_with(prefix)
        flat_list = []
        for r in results:
            for item in r["data"]:
                if item not in flat_list:
                    flat_list.append(item)
        return flat_list
