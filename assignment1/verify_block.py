import hashlib
import json 
import re
import sys

TARGET_DIFFICULTY = 2**240 

# 해시 변환 함수 
def calculate_hash(block_data):
    block_string = json.dumps(block_data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(block_string).hexdigest()

# 텍스트 파일에서 블록 데이터 파싱 
def parse_block_file(filename):
    data = {}
    tx_content  = "" 

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"오류 : 파일을 찾을 수 없습니다. ({filename})")
        return None 
    
    for line in lines:
        line = line.strip()
        if not line: 
            continue

        if line.startswith("Block:"):
            data['Block'] = int(line.split(':')[1].strip())
        elif line.startswith("Nonce:"):
            data['Nonce'] = int(line.split(':')[1].strip().replace(',', ''))
        elif line.startswith("Prev:"):
            data['Prev'] = line.split(':')[1].strip()
        elif line.startswith("Tx:"):
            tx_content  = line.split(':', 1)[1].strip()
        elif line.startswith("Final Hash:"):
            data['FileHash'] = line.split(':')[1].strip()

    
    if tx_content:
        # Tx: $ [Amount] From: [Sender] -> [Recipient] 형식에서 추출
        try:
            # 'From:'과 '->'를 기준으로 분리하여 Sender와 Recipient 추출
            parts = tx_content.split(' From: ')
            amount_part = parts[0].replace('$', '').strip() # $ 50 -> 50
            
            sender_recipient_part = parts[1]
            sender_name = sender_recipient_part.split(' -> ')[0].strip() # Alice
            recipient_name = sender_recipient_part.split(' -> ')[1].strip() # Bob
            
            data['Amount'] = amount_part
            data['Sender'] = sender_name
            data['Recipient'] = recipient_name
            
        except IndexError:
            print(f"경고: {filename}의 Tx 데이터를 분리하는 중 오류가 발생했습니다. Tx 내용: '{tx_content}'")
            return None

    if not all(k in data for k in ['Block', 'Nonce', 'Prev', 'Amount', 'Sender', 'Recipient']):
        print(f"오류: {filename}에 필수 블록 정보가 부족합니다.")
        return None 
    return data 

# 실행 
def main():
    if len(sys.argv) != 2:
        print("사용법; python verify_block.py <BlockN.txt>")
        sys.exit(1)

    filename = sys.argv[1] 

    # 파일에서 데이터 추출 
    parsed_data = parse_block_file(filename)
    if not parsed_data:
        return 
    
    print(f"\n 블록 유효성 검사 시작 : {filename}")

    # 해시 재계산을 위한 블록 데이터 재구성 
    block_data_for_hash = {
        "Block": parsed_data['Block'],
        "Tx": {
            "S": parsed_data['Amount'],
            "From": parsed_data['Sender'],
            "To": parsed_data['Recipient']
        },
        "Prev": parsed_data['Prev'],
        "Nonce": parsed_data['Nonce'] 
    }

    # 해시 재계산 
    recalculated_hash = calculate_hash(block_data_for_hash)

    # 난이도 검증 
    is_valid_pow = int(recalculated_hash, 16) < TARGET_DIFFICULTY

    # 결과 출력 
    print(f"Nonce: {parsed_data['Nonce']:,}")
    print(f"Prev Hash: {parsed_data['Prev']}")
    print(f"재계산된 Hash: {recalculated_hash}")
    
    if 'FileHash' in parsed_data:
        hash_match = (parsed_data['FileHash'] == recalculated_hash)
        print(f"  파일에 기록된 Hash: {parsed_data['FileHash']}")
        print(f"  해시 일치 여부: {'✅ 일치' if hash_match else '❌ 불일치'}")
        
        if not hash_match:
             print("경고: 파일에 기록된 해시와 재계산된 해시가 다릅니다. 데이터가 손상되었거나 계산 방식이 다릅니다!")

    print("\n--- 유효성 검증 결과 ---")
    if is_valid_pow:
        print(f"🎉 블록 유효 (PoW 성공): 해시 < 2^{240} 조건을 만족합니다.")
    else:
        print(f"❌ 블록 무효 (PoW 실패): 해시가 2^{240} 조건을 만족하지 못합니다.")

if __name__ == "__main__":
    main()