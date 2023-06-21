import sqlite3

# Connect to the database
conn = sqlite3.connect('dev.sqlite')
cursor = conn.cursor()

# Retrieve the image data from the database
cursor.execute("SELECT ImageData FROM Images WHERE ImageId = ?", (1,))
image_data = cursor.fetchone()[0]

# Save the image data to a file
with open('retrieved_image.jpg', 'wb') as file:
    file.write(image_data)

# Close the connection
conn.close()
