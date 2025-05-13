import streamlit as st
import json
from langchain_core.messages import HumanMessage, AIMessage
from travel_planner import travel_planner, search_hotels, get_hotel_details, print_hotel_details
from travel_planner import app
import streamlit.components.v1 as components


def main():
    st.title("Travel Planner")

    # Place Input
    place = st.text_input("Where do you want to go?")

    # Days Slider
    num_days = st.slider("Number of days", 1, 20, 0)

    # Specific places (comma-separated)
    specific_places = st.text_input("Specific places to visit (comma-separated)")

    # Initialize session state
    if 'itinerary' not in st.session_state:
        st.session_state['itinerary'] = ""
    if 'hotels' not in st.session_state:
        st.session_state['hotels'] = []

    # Create Itinerary Button
    if st.button("Create Itinerary"):
        if place and num_days:
            interests = [interest.strip() for interest in specific_places.split(',') if interest.strip()]
            user_request = f"Plan a {num_days}-day trip to {place} with interests: {', '.join(interests)}"

            state = {
                "messages": [HumanMessage(content=user_request)],
                "city": place,
                "days": num_days,
                "interests": interests,
                "itinerary": "",
            }

            # Generate itinerary using the travel planner function
            final_state = app.invoke(state)

            # Save itinerary to session state
            if final_state and final_state['itinerary']:
                st.session_state['itinerary'] = final_state['itinerary']
            else:
                st.warning("Failed to generate an itinerary. Please try again.")
        else:
            st.warning("Please enter the destination and number of days.")

    # Show itinerary if available
    if st.session_state['itinerary']:
        st.subheader("Your Travel Itinerary")
        st.markdown(st.session_state['itinerary'].replace('\n', '\n\n'))

    # Recommend Hotels Button
    if st.button("Recommend Hotels"):
        if place:
            hotels = search_hotels(place)
            if hotels:
                st.session_state['hotels'] = hotels
            else:
                st.warning("No hotels found for this location.")
        else:
            st.warning("Please enter a place first.")

    # Show hotels if available
    if st.session_state['hotels']:
        st.subheader("Hotel Recommendations")
        for hotel in st.session_state['hotels'][:min(5, len(st.session_state['hotels']))]:
            if hotel.get('type') == 'accommodation':
                image_url = hotel.get('featured_image', "https://placehold.it/20x20")
                hotel_name = hotel.get('name') or 'Unnamed Hotel'
                hotel_link = hotel.get('link') or '#'
                
                # Show image with clickable link
                st.markdown(f"[{hotel_name}]({hotel_link})")
                st.write(f"**{hotel_name}**")
                st.write(f"ID: {hotel.get('id', 'N/A')}")
                st.write("---")

    # Hotel ID Input
    hotel_id = st.text_input("Enter Hotel ID for details")

    # Get Hotel Details
    if hotel_id:
        details = get_hotel_details(hotel_id)
        if details:
            st.subheader("Hotel Details")
            st.write(f"Name: {details.get('name', 'N/A')} ⭐ ({details.get('reviews', 'N/A')} reviews)")
            st.write(f"Rating: {details.get('rating', 'N/A')}")
            st.write(f"Address: {details.get('address', 'N/A')}")
            st.write(f"Phone: {details.get('phone', 'N/A')}")
            st.write(f"Email: {details.get('email', 'N/A')}")
            st.write(f"Website: {details.get('website', 'N/A')}")
            st.write(f"TripAdvisor Link: {details.get('link', 'N/A')}")
            #st.write(f"Location: 📍 {details.get('latitude', 'N/A')}, {details.get('longitude', 'N/A')}")
            latitude = details.get('latitude', 'N/A')
            longitude = details.get('longitude','N/A')
            if latitude != 'N/A' and longitude != 'N/A':
                map_url = f"https://www.google.com/maps?q={latitude},{longitude}&output=embed"
                html_code = f"""
                <div style="display: flex; justify-content: center;">
                    <iframe
                        width="100%"
                        height="500"
                        frameborder="0"
                        style="border:0; border-radius: 10px;"
                        src="{map_url}"
                        allowfullscreen>
                    </iframe>
                </div>
                """
                components.html(html_code, height=520)
            else:
                st.write("Location: 📍 N/A")
            ranking = details.get('ranking', {})
            st.write("\n🏅 Ranking:")
            st.write(f"Current Rank: {ranking.get('current_rank', 'N/A')} out of {ranking.get('total', 'N/A')} hotels")

            reviews_per_rating = details.get('reviews_per_rating', {})
            st.write("\n📝 Reviews Breakdown:")
            for rating, count in reviews_per_rating.items():
                st.write(f"{rating} stars: {count} reviews")

            review_keywords = details.get('review_keywords', [])
            st.write("\n🔑 Popular Keywords:")
            keywords = ', '.join(review_keywords[:10])
            st.write(f"{keywords}...")
            #st.write(f"\n🖼️ Featured Image: {details.get('featured_image', 'N/A')}")
            image_url = details.get('featured_image', 'N/A')
            hotel_name = details.get('name', 'Unnamed Hotel')

            if image_url != 'N/A':
                st.image(image_url, caption=hotel_name, use_column_width=True)
            else:
                st.write("🖼️ Featured Image: N/A")
                
   
if __name__ == "__main__":
    main()
