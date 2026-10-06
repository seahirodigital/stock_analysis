
import os

def fix_encoding(directory):
    # 文字化け特有の文字（Shift-JISをUTF-8と誤認して保存した際に現れる代表的な文字）
    # 豬√ (流), 縺 (し/た等), 繧 (あ/い等), 蜿 (か), 蜷 (な)
    MOJIBAKE_SYMPTOMS = ['豬√', '縺', '繧', '蜿', '蜷', '縲', '縺吶', '縺ｾ']

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "SKILL.md":
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
                
                if not raw_data:
                    continue
                
                print(f"Checking: {file_path}")
                
                text = None
                is_mojibake = False
                
                try:
                    # まずUTF-8として読み込む
                    temp_text = raw_data.decode('utf-8')
                    
                    # 内容に文字化け症状があるかチェック
                    if any(symptom in temp_text for symptom in MOJIBAKE_SYMPTOMS):
                        print("  Detected mojibake symptoms in UTF-8. Attempting to recover...")
                        # 誤ってUTF-8で保存されたShift-JISデータを復元する魔法:
                        # UTF-8文字列 -> 各文字をlatin-1(bytes)に変換 -> それをcp932としてデコード
                        try:
                            # 一旦 latin-1 でバイト列に戻すことで、元のバイト列（に近いもの）を得る
                            # ただし、保存時に不正なUTF-8シーケンスとして欠落している場合は完全復元不可
                            recovered_bytes = temp_text.encode('latin-1', errors='ignore')
                            text = temp_text.encode('utf-8').decode('utf-8').encode('iso-8859-1').decode('cp932')
                        except:
                            # 上記がダメな場合、素直にバイト列からの変換を試みる
                            try:
                                text = raw_data.decode('cp932')
                            except:
                                # 最終手段
                                pass
                        is_mojibake = True
                    else:
                        text = temp_text
                except UnicodeDecodeError:
                    # UTF-8でデコードすらできない場合は純粋なShift-JISの可能性が高い
                    try:
                        print("  UnicodeDecodeError. Trying CP932...")
                        text = raw_data.decode('cp932')
                    except:
                        print("  Failed to decode as CP932.")
                        continue

                # 判定: textに文字化けが残っていないか再チェック
                if text and any(symptom in text for symptom in MOJIBAKE_SYMPTOMS):
                     # まだ化けている場合、別の復元ロジックを試す
                     try:
                         # encode utf-8 -> decode latin-1 -> encode utf-8 -> decode cp932 的な試行錯誤
                         # ここではシンプルにバイト列から直で行く
                         text = raw_data.decode('cp932', errors='replace')
                     except:
                         pass

                if text:
                    # 結果が正常っぽいか（特定の予約語などが含まれているか）
                    if 'name:' in text or '#' in text:
                        try:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(text)
                            print(f"  Result: Fixed and saved as UTF-8.")
                        except Exception as e:
                            print(f"  Error writing {file_path}: {e}")
                    else:
                        print("  Recovery seems invalid (missing metadata). Skipping.")

if __name__ == "__main__":
    target_dir = r"c:\Users\HCY\OneDrive\事業\事業開発スキル\finance"
    fix_encoding(target_dir)
