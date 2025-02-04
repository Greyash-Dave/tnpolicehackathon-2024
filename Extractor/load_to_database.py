from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase credentials. Please check your .env file")

print(f"Connecting to Supabase URL: {supabase_url[:20]}...")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Failed to create Supabase client: {str(e)}")
    exit(1)

# Sample data
posts_data = {
    "Posts": [
        {
            "name": "John Memes",
            "username": "@temitopek66",
            "description": "#memecoin #México #Sinaloa #Terrorismo #Culiacán #Ad #Bitcoin #Doge #Investing #Financial #Crypto #Blockchain #Altcoins #Tech #memecoin #vet #eth #Defi #Web3 #Torn #Tron",
            "date": "Dec 4, 2024"
        },
        {
            "name": "poet.base.eth",
            "username": "@1CrypticPoet",
            "description": "🔥 New Ripple Ad 🔥\n\nCheck it out‼️\n\nhttps://youtu.be/unl6T2Zctgw #XRP #XRPCommunity #crypto #blockchain",
            "date": "Nov 25, 2020"
        },
        {
            "name": "poet.base.eth",
            "username": "@1CrypticPoet",
            "description": "🔥 Ripple just released a new marketing ad.\n\nCheck it out!\n\nhttps://youtu.be/48_0uAtpliM #xrp $xrp #XRPCommunity #crypto #blockchain",
            "date": "Jan 19, 2023"
        },
        {
            "name": "AdPod",
            "username": "@AdPodxyz",
            "description": "The only thing common about everything viral in #crypto?\n\nThey don't just stumble onto the #attention meter. 🎯\n\nBehind every pump, every #meme, every moonshot lies a well-calculated plan.\n\nAt AdPod, we know strategy wins the game.\n\nSmart #targeting. Smarter #execution. 🚀",
            "date": "Dec 11, 2024"
        },
        {
            "name": "polaR 🐻‍❄️",
            "username": "@web3Polar",
            "description": "1x Winner $SOL or $ETH • 24 Hours⏱️\n\n• RT + Like 🔔\n• Comment \"Done\"\n\n#Crypto #Memecoin #SolanaGiveaway #NFTs #ETH #NFTCommunity #ad #SOL #Giveaway",
            "date": "Dec 6, 2024"
        }
    ]
}


def parse_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%b %d, %Y")
        return date_obj.isoformat()
    except ValueError as e:
        print(f"Error parsing date {date_str}: {e}")
        return date_str

def upload_to_supabase():
    success_count = 0
    failure_count = 0
    
    print("\nStarting upload process...")
    
    for post in posts_data["Posts"]:
        try:
            # Create a copy of the post to modify
            upload_post = post.copy()
            
            # Parse the date
            upload_post["date"] = parse_date(upload_post["date"])
            
            print(f"\nUploading post for {upload_post['username']}...")
            print(f"Data to be uploaded: {upload_post}")
            
            # Attempt to insert the data
            response = supabase.table("posts").insert(upload_post).execute()
            
            if hasattr(response, 'data') and response.data:
                print(f"✅ Successfully uploaded post from {upload_post['username']}")
                success_count += 1
            else:
                print(f"❌ Failed to upload post from {upload_post['username']}")
                print(f"Response: {response}")
                failure_count += 1
                
        except Exception as e:
            print(f"❌ Error uploading post from {post['username']}: {str(e)}")
            failure_count += 1
            
    print(f"\nUpload Summary:")
    print(f"Successful uploads: {success_count}")
    print(f"Failed uploads: {failure_count}")
    print(f"Total posts processed: {len(posts_data['Posts'])}")

def verify_data():
    print("\nVerifying uploaded data...")
    try:
        result = supabase.table("posts").select("*").execute()
        if hasattr(result, 'data'):
            print(f"Found {len(result.data)} posts in database:")
            for post in result.data:
                print(f"\nName: {post['name']}")
                print(f"Username: {post['username']}")
                print(f"Date: {post['date']}")
        else:
            print("No data found in the database")
    except Exception as e:
        print(f"Error verifying data: {str(e)}")

def main():
    print("Starting data upload to Supabase...")
    upload_to_supabase()
    verify_data()
    print("\nProcess completed!")

if __name__ == "__main__":
    main()