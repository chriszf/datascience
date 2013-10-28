import pymongo

client = pymongo.MongoClient()

def main():
    f = open("train_triplets.txt")
    last_user_id = None
    users = client.datascience.users
    for line in f:
        user_id, song, plays = line.split()
        if user_id != last_user_id:
            pass

        # insert a record into the users collection

if __name__ == "__main__":
    main()
