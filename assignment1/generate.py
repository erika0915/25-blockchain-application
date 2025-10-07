import hashlib
import json 
import time

# 거래 데이터 
TRANSACTIONS = [
    ("50", "Alice", "Bob"),
    ("120", "Carol", "Dave"), 
    ("7.25", "Eve", "Frank"), 
    ("250", "Grace", "Heidi"), 
    ("15", "Ivan", "Judy"), 
    ("999.99", "Karl", "Laura"), 
    ("3.50", "Mallory", "Nathan"),
    ("45", "Olivia", "Paul"), 
    ("60", "Quinn", "Rachel"), 
    ("180", "Steve", "Trudy") 
]
TARGET_DIFFICULTY = 2**240 

# 해시 계산 함수 
def calculate_hash(block_data):
    block_string = json.dumps(block_data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(block_string).hexdigest()

# 작업 증명 함수 
def mine_block(index, amount, sender, recipient, previous_hash):
    
    print(f"\n--- [{index}번 블록] 채굴 시작 ---")
    
    nonce = 0
    start_time = time.time()
    
    while True:
        block_data = {
            "Block": index,
            "Tx": {
                "S": amount,
                "From": sender,
                "To": recipient
            },
            "Prev": previous_hash,
            "Nonce": nonce 
        }
        
        # 해시 계산
        current_hash = calculate_hash(block_data)

        # 난이도 검증 
        if int(current_hash, 16) < TARGET_DIFFICULTY:
            end_time = time.time()
            
            print(f"[{index}번 블록] 채굴 성공!")
            print(f"  Nonce: {nonce:,}")
            print(f"  Hash: {current_hash}")
            print(f"  Time taken: {end_time - start_time:.4f} seconds")
            
            # 성공한 블록 데이터와 최종 해시를 반환
            return block_data, current_hash
        
        nonce += 1

# 실행 
def main():
    prev_hash = "0" * 64 

    for i, tx_data in enumerate(TRANSACTIONS, start=1):
        amount, sender, recipient = tx_data
        
        block, block_hash = mine_block(i, amount, sender, recipient, prev_hash)

        filename = f"Block{i}.txt"
        with open(filename, "w") as f:

            output = f"Block: {block['Block']}\n"
            output += f"Nonce: {block['Nonce']}\n"
            output += f"Tx: $ {block['Tx']['S']} From: {block['Tx']['From']} -> {block['Tx']['To']}\n"
            output += f"Prev: {block['Prev']}\n"
            output += f"Final Hash: {block_hash}\n"
            f.write(output)
        
        print(f"  -> 파일 저장 완료: {filename}")

        prev_hash = block_hash 

    print("\n 모든 10개 블록이 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    main()