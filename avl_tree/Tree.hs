import Prelude hiding (lookup)

-- Implement a binary search tree (4 points)
-- 2 extra points for a balanced tree
-- AVL tree
data BinaryTree k v = Nil | Node (k, v) (BinaryTree k v) (BinaryTree k v) Int deriving Show

makeTree :: (k, v) -> BinaryTree k v -> BinaryTree k v -> BinaryTree k v
makeTree kv l r = Node kv l r ((max (getHeight l) (getHeight r)) + 1)

getHeight :: BinaryTree k v -> Int
getHeight Nil = 0
getHeight (Node _ _ _ h) = h

-- “Ord k =>” requires, that the elements of type k are comparable
-- Takes a key and a tree and returns Just value if the given key is present,
-- otherwise returns Nothing
lookup :: Ord k => k -> BinaryTree k v -> Maybe v
lookup _ Nil = Nothing
lookup key (Node (k, v) l r _)
    | key < k = lookup key l
    | key > k = lookup key r
    | otherwise = Just v

-- Takes a key, value and tree and returns a new tree with key/value pair inserted.
-- If the given key was already present, the value is updated in the new tree.
insert :: Ord k => k -> v -> BinaryTree k v -> BinaryTree k v
insert key value Nil = makeTree (key, value) Nil Nil
insert key value (Node (k, v) l r h)
    | key < k = balance (k, v) (insert key value l) r
    | key > k = balance (k, v) l (insert key value r)
    | otherwise = Node (key, value) l r h

-- Returns a new tree without the given key
delete :: Ord k => k -> BinaryTree k v -> BinaryTree k v
delete _ Nil = Nil
delete key (Node (k, v) l r _)
    | key < k = balance (k, v) (delete key l) r
    | key > k = balance (k, v) l (delete key r)
    | otherwise = merge l r
    where
        merge :: BinaryTree k v -> BinaryTree k v -> BinaryTree k v
        merge l Nil = l
        merge l r   = balance (getMin r) l (deleteMin r)

        getMin :: BinaryTree k v -> (k, v)
        getMin (Node kv Nil _ _) = kv
        getMin (Node _  l   _ _) = getMin l
        
        deleteMin :: BinaryTree k v -> BinaryTree k v
        deleteMin (Node _  Nil r _) = r
        deleteMin (Node kv l   r _) = balance kv (deleteMin l) r

balance :: (k, v) -> BinaryTree k v -> BinaryTree k v -> BinaryTree k v
balance kv l r
    | balanceFactor == 2 && rightBalanceFactor >= 0 = leftRotate kv l r
    | balanceFactor == 2 && rightBalanceFactor <  0 = leftBigRotate kv l r
    | balanceFactor == -2 && leftBalanceFactor <= 0 = rightRotate kv l r
    | balanceFactor == -2 && leftBalanceFactor >  0 = rightBigRotate kv l r
    | otherwise = makeTree kv l r
    where
        leftRotate :: (k, v) -> BinaryTree k v -> BinaryTree k v -> BinaryTree k v
        leftRotate p a (Node q b c _) = makeTree q (makeTree p a b) c
        
        rightRotate :: (k, v) -> BinaryTree k v -> BinaryTree k v -> BinaryTree k v
        rightRotate q (Node p a b _) c = makeTree p a (makeTree q b c)
        
        leftBigRotate :: (k, v) -> BinaryTree k v -> BinaryTree k v -> BinaryTree k v
        leftBigRotate p a (Node q (Node s b c _) d _) = makeTree s (makeTree p a b) (makeTree q c d)
        
        rightBigRotate :: (k, v) -> BinaryTree k v -> BinaryTree k v -> BinaryTree k v
        rightBigRotate q (Node p a (Node s b c _) _) d = makeTree s (makeTree p a b) (makeTree q c d)

        balanceFactor1 :: BinaryTree k v -> Int
        balanceFactor1 (Node _ l r _) = balanceFactor2 l r
        
        balanceFactor2 :: BinaryTree k v -> BinaryTree k v -> Int
        balanceFactor2 l r = (getHeight r) - (getHeight l)

        balanceFactor = balanceFactor2 l r
        leftBalanceFactor = balanceFactor1 l
        rightBalanceFactor = balanceFactor1 r
