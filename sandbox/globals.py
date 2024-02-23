debian_releases = ["jessie", "stretch", "buster", "bullseye", "bookworm"]
debian_images = [f"debian:{release}" for release in debian_releases]
linux_images = debian_images