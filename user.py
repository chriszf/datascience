import pymongo

client = pymongo.MongoClient()

def main():
    f = open("train_triplets.txt")
    last_user_id = None
    users = client.datascience.users
    users.remove() # Erase the existing collection

    for line in f:
        user_id, song_id, plays = line.split()
        plays = int(plays)
        if user_id != last_user_id:
            user = {"user_id": user_id, songs = []}
        user['songs'].append({"song_id": song_id,
                              "plays": plays})

        users.insert(user)

if __name__ == "__main__":
    main()
