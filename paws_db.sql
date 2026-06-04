-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: paws_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `adoption_applications`
--

DROP TABLE IF EXISTS `adoption_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adoption_applications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `pet_id` int NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `location` varchar(255) NOT NULL,
  `aadhar_path` varchar(255) DEFAULT '',
  `home_type` varchar(100) NOT NULL,
  `has_pets` varchar(50) NOT NULL,
  `reason` text NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `applied_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `meeting_time` varchar(100) DEFAULT NULL,
  `rejection_reason` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `pet_id` (`pet_id`),
  CONSTRAINT `adoption_applications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `adoption_applications_ibfk_2` FOREIGN KEY (`pet_id`) REFERENCES `pets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adoption_applications`
--

LOCK TABLES `adoption_applications` WRITE;
/*!40000 ALTER TABLE `adoption_applications` DISABLE KEYS */;
INSERT INTO `adoption_applications` VALUES (101,1,1,'Rahul','rahul@gmail.com','9876543210','Hyderabad','/uploads/rahul_aadhar.pdf','Apartment','Yes','I love dogs and want to give Bruno a safe home.','Pending','2026-05-25 06:08:18',NULL,NULL),(102,1,6,'Priya','priya@gmail.com','9876543211','Secunderabad','/uploads/priya_aadhar.pdf','Independent House','No','I live alone and want Luna as my companion.','Approved','2026-05-25 06:08:18',NULL,NULL),(103,1,2,'Arjun','arjun@gmail.com','9876543212','Gachibowli','/uploads/arjun_aadhar.pdf','Farm / Open Space','Yes','We have a farm and Rocky can run freely here.','Approved','2026-05-25 06:08:18','2026-09-12 at 13:55',NULL),(104,1,9,'Rachel','Rachel@gmail.com','85198 47264','vikarabad','/static/uploads/1779779186_WhatsApp Image 2026-03-30 at 9.53.24 AM.jpeg','Independent House','No','i love animals','Approved','2026-05-26 07:06:26','2026-05-30 at 15:41',NULL),(105,13,7,'Rachel','rachelboyajula7@gmail.com','06300104515','vikarabad','/static/uploads/1779785827_WhatsApp Image 2026-01-19 at 2.30.01 PM.jpeg','Apartment','Yes','love animals','Pending','2026-05-26 08:57:07',NULL,NULL);
/*!40000 ALTER TABLE `adoption_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_care`
--

DROP TABLE IF EXISTS `medical_care`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_care` (
  `id` int NOT NULL AUTO_INCREMENT,
  `case_name` varchar(255) NOT NULL,
  `animal_type` varchar(100) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `description` text,
  `vet_assigned` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_care`
--

LOCK TABLES `medical_care` WRITE;
/*!40000 ALTER TABLE `medical_care` DISABLE KEYS */;
INSERT INTO `medical_care` VALUES (1,'Fractured Dog Leg','Dog','Ongoing','Street dog found near Gachibowli with a fractured hind leg.','Dr. K. S. Rao'),(2,'Dehydrated Kitten','Cat','Recovered','A 2-month-old kitten found severely dehydrated.','Dr. K. S. Rao'),(3,'Injured Eagle','Bird','Pending','Eagle found with wing lacerations.',NULL);
/*!40000 ALTER TABLE `medical_care` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ngo_members`
--

DROP TABLE IF EXISTS `ngo_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ngo_members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `role` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ngo_members`
--

LOCK TABLES `ngo_members` WRITE;
/*!40000 ALTER TABLE `ngo_members` DISABLE KEYS */;
INSERT INTO `ngo_members` VALUES (1,'Ramesh Kumar','Rescue Specialist','ramesh@paws.org','9848012345'),(2,'Suresh Raina','Medical Coordinator','suresh@paws.org','9848012346'),(3,'Mahesh Babu','Shelter Manager','mahesh@paws.org','9848012347'),(4,'karthik jakkula','Rescue Specialist','karthikjakkula840@gmail.com','09063693457'),(5,'M.vinay','Medical Coordinator','vinay@gmail.com','90636 93457'),(6,'M.vikram','Rescue Specialist','vikram@gmail.com','90636 93457'),(7,'preethi','Shelter Manager','rachelboyajula7@gmail.com','6300104515');
/*!40000 ALTER TABLE `ngo_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pets`
--

DROP TABLE IF EXISTS `pets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(100) NOT NULL,
  `gender` varchar(50) NOT NULL,
  `age` int NOT NULL,
  `weight` varchar(50) NOT NULL,
  `breed` varchar(100) NOT NULL,
  `location` varchar(255) NOT NULL,
  `health` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `personality` varchar(100) DEFAULT '',
  `energy_level` varchar(100) DEFAULT '',
  `good_with_kids` varchar(50) DEFAULT 'Yes',
  `favorite_food` varchar(100) DEFAULT '',
  `favorite_toy` varchar(100) DEFAULT '',
  `training` varchar(100) DEFAULT '',
  `image_filename` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Available',
  `uploaded_by` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pets`
--

LOCK TABLES `pets` WRITE;
/*!40000 ALTER TABLE `pets` DISABLE KEYS */;
INSERT INTO `pets` VALUES (1,'Bruno','Dog','Male',2,'20 kg','Australian Shepherd','Green Park Animal Shelter, Banjara Hills, Hyderabad, Telangana','Vaccinated','Bruno is a friendly and energetic dog who loves outdoor activities and playing with people. He is well-trained, healthy, and very social with other pets. Buddy enjoys running, exploring new places, and spending time with his human companions.','Friendly','High','Yes','Chicken','Tennis Ball','Basic Trained','https://i.postimg.cc/cLdfD6Lc/Dog-image.png','Available',NULL),(2,'Luna','Cat','Female',1,'4 kg','Domestic Shorthair','Shelter Rescue Center, Hyderabad','Vaccinated','Luna is a quiet, sweet cat who loves to cuddle and nap. She gets along well with other cats.','Calm','Low','Yes','Fish','Feather Wand','Litter Trained','https://i.postimg.cc/c4n31wrX/cat1.png','Adopted',NULL),(3,'Rocky','Dog','Male',3,'15 kg','Indie Breed','Shelter Rescue Center, Hyderabad','Vaccinated','Rocky is a loyal guard dog who is extremely active and protective. Needs an active owner.','Protective','High','No','Pedigree','Chew Toy','None','https://i.postimg.cc/BbgntZfq/parrot1.png','Pending',NULL),(4,'Milo','Cat','Male',1,'5 kg','Persian','Shelter Rescue Center, Hyderabad','Healthy','Milo is a beautiful, long-haired Persian cat who loves attention. Very playful.','Playful','Medium','Yes','Salmon Cat Food','Laser Pointer','Litter Trained','https://i.postimg.cc/6QmR50fB/dog2.png','Available',NULL),(5,'Bella','Puppy','Female',1,'8 kg','Labrador Retriever','Shelter Rescue Center, Hyderabad','Vaccinated & De-wormed','Bella is a lovable puppy looking for her forever home. She is highly trainable and friendly.','Lovable','High','Yes','Milk Biscuits','Squeaky Toy','Housebroken','https://i.postimg.cc/gkmwpQb6/Rabbit.png','Available',NULL),(6,'Snowy','Cat','Female',2,'4.5 kg','Siamese','Shelter Rescue Center, Hyderabad','Healthy','Snowy is an affectionate Siamese cat who has already been successfully adopted.','Affectionate','Medium','Yes','Wet Food','Ball of Yarn','Litter Trained','https://i.postimg.cc/dVFjz44n/cat2.png','Adopted',NULL),(7,'Baby','Dog','Male',4,'N/A','','KPHP','Healthy','healthy,good behaviour with humans','','','Yes','','','','/static/uploads/1779769993_adopted-pets-april-44-6449168a12d3c__700.jpg','Pending',NULL),(8,'luna','Dog','Female',3,'N/A','German shetherd','vikarabad','Healthy','nice','','','Yes','','','','/static/uploads/1779770469_OIP.jpg','Available',NULL),(9,'chinni','rabbit','Female',2,'N/A','','kukatpally','Healthy','friendly','','','Yes','','','','/static/uploads/1779779004_Exotic-Pets-img.jpg','Adopted',NULL);
/*!40000 ALTER TABLE `pets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reports`
--

DROP TABLE IF EXISTS `reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `image_filename` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `lat` decimal(10,8) DEFAULT NULL,
  `lng` decimal(11,8) DEFAULT NULL,
  `map_link` text,
  `description` text NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `reported_by` int DEFAULT NULL,
  `reported_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `assigned_to` int DEFAULT NULL,
  `rejection_reason` text,
  `resolved_image_filename` varchar(255) DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `reported_by` (`reported_by`),
  KEY `assigned_to` (`assigned_to`),
  CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`reported_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `reports_ibfk_2` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reports`
--

LOCK TABLES `reports` WRITE;
/*!40000 ALTER TABLE `reports` DISABLE KEYS */;
INSERT INTO `reports` VALUES (1,'https://images.unsplash.com/photo-1596492784531-6e6eb5ea9993','Kukatpally, Hyderabad',17.48340000,78.38620000,'https://maps.google.com/?q=17.4834,78.3862','Street dog hit by a vehicle, limping badly.','Completed',1,'2026-05-25 06:08:18',5,NULL,''),(2,'https://images.unsplash.com/photo-1573865526739-10659fec78a5','Ameerpet, Hyderabad',17.43750000,78.44820000,'https://maps.google.com/?q=17.4375,78.4482','Stray cat trapped in a drain pipe.','Assigned',NULL,'2026-05-25 06:08:18',6,NULL,''),(3,'/static/uploads/1779689492_How-to-take-care-of-injured-or-orphaned-animals-.jpg','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','head injred\r\n','Completed',1,'2026-05-25 06:11:32',9,NULL,''),(4,'/static/uploads/1779689602_How-to-take-care-of-injured-or-orphaned-animals-.jpg','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','leg fracture\r\n','Pending',1,'2026-05-25 06:13:22',NULL,NULL,''),(5,'/static/uploads/1779690513_paws-in-peril-eam-levi_1200_62631efd-38e0-4587-bb59-c05983e49497.webp','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','mouth infaction','Rejected',1,'2026-05-25 06:28:33',7,'fsdfsdf',''),(6,'/static/uploads/1779691486_paws-in-peril-eam-levi_1200_62631efd-38e0-4587-bb59-c05983e49497.webp','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','head fracture\r\n','Pending',1,'2026-05-25 06:44:46',NULL,NULL,''),(7,'/static/uploads/1779768571_AnimalMedHospital-1-1-2000x1333.jpg','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','head','Assigned',1,'2026-05-26 04:09:31',8,NULL,''),(14,'/static/uploads/1779770265_Helping-Injured-Wildlife.jpg','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','eye injured','Pending',1,'2026-05-26 04:37:45',NULL,NULL,''),(15,'/static/uploads/1779772160_OIP.webp','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','leg injured\r\n','Completed',1,'2026-05-26 05:09:20',9,NULL,''),(16,'/static/uploads/1779772913_OIP.webp','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','leg fracure','Pending',1,'2026-05-26 05:21:53',NULL,NULL,''),(17,'/static/uploads/1779773276_OIP.webp','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','leg fracure','Pending',1,'2026-05-26 05:27:56',NULL,NULL,''),(18,'/static/uploads/1779777868_OIP.jpg','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','fsdfsdfsdfdsf','Completed',1,'2026-05-26 06:44:28',7,NULL,''),(19,'/static/uploads/1779785713_Exotic-Pets-img.jpg','Atevelle, Medchal mandal, Medchal–Malkajgiri, Telangana, 501400, India',17.64430000,78.49220000,'https://www.google.com/maps?q=17.6443,78.4922','eye problem','Completed',13,'2026-05-26 08:55:13',10,NULL,'');
/*!40000 ALTER TABLE `reports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shelters`
--

DROP TABLE IF EXISTS `shelters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shelters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `contact` varchar(50) NOT NULL,
  `capacity` int NOT NULL,
  `occupied` int NOT NULL DEFAULT '0',
  `description` text,
  `image_filename` varchar(255) DEFAULT '',
  `status` varchar(50) DEFAULT 'Active',
  `delete_reason` varchar(255) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shelters`
--

LOCK TABLES `shelters` WRITE;
/*!40000 ALTER TABLE `shelters` DISABLE KEYS */;
INSERT INTO `shelters` VALUES (1,'Green Park Animal Shelter','Banjara Hills, Hyderabad','040-12345678',50,15,'A spacious shelter equipped with play areas and vet care.','https://images.unsplash.com/photo-1548767797-d8c844163c4c','Active',''),(2,'Paws Rescue Home','Secunderabad, Hyderabad','040-87654321',30,8,'Cozy shelter specializing in feline rescue and rehabilitation.','https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba','Active',''),(3,'Hope Shelter Rescue Center','Gachibowli, Hyderabad','040-99998888',40,20,'State-of-the-art facility for trauma rehabilitation.','https://images.unsplash.com/photo-1570129477492-45c003edd2be','Active',''),(4,'Breath Animal Rescue Home','Breath Animal Rescue Home, Bowrampet, Dundigal, opposite to Sri Engineers concrete, Hyderabad, Telangana 500043','040-12345678',200,0,'','1779780355_Screenshot 2026-05-26 125443.png','Deleted','not good'),(5,'Jeeva Vaatsalya Rescue and Rehabilitation Center','Jeeva Vaatsalya Rescue, Bachupally, Hyderabad','040-12345678',200,0,'','1779787186_6822f3fef67ae27b38635295_1747121150078.jpg','Deleted','ff');
/*!40000 ALTER TABLE `shelters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'user',
  `location` varchar(255) DEFAULT '',
  `profile_img` varchar(255) DEFAULT '',
  `capacity` int DEFAULT '50',
  `cases` int DEFAULT '0',
  `status` varchar(50) DEFAULT 'Active',
  `delete_reason` varchar(255) DEFAULT '',
  `joined_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Ajay User','user@gmail.com','9876543210','user123','user','Hyderabad','https://i.postimg.cc/hjWXK1Mv/killuva.jpg',50,0,'Active','','2026-05-25 06:08:18'),(2,'Admin User','admin@gmail.com','9876543211','admin123','admin','Delhi','https://img.magnific.com/free-vector/young-man-with-glasses-avatar_1308-175763.jpg?semt=ais_hybrid&w=740&q=80',50,0,'Active','','2026-05-25 06:08:18'),(3,'NGO Representative','ngo@gmail.com','9876543212','ngo123','ngo','Mumbai','https://img.magnific.com/free-vector/young-man-with-glasses-avatar_1308-175763.jpg?semt=ais_hybrid&w=740&q=80',50,0,'Active','','2026-05-25 06:08:18'),(4,'Rescue Team Lead','rescue@gmail.com','9876543213','rescue123','rescue','Bangalore','https://img.magnific.com/free-vector/young-man-with-glasses-avatar_1308-175763.jpg?semt=ais_hybrid&w=740&q=80',50,0,'Active','','2026-05-25 06:08:18'),(5,'Ramesh Kumar','ramesh@paws.org','9848012345','rescue123','rescue','Hyderabad','',50,0,'Active','','2026-05-25 06:08:18'),(6,'Suresh Raina','suresh@paws.org','9848012346','rescue123','rescue','Hyderabad','',50,0,'Active','','2026-05-25 06:08:18'),(7,'Mahesh Babu','mahesh@paws.org','9848012347','rescue123','rescue','Hyderabad','',50,0,'Active','','2026-05-25 06:08:18'),(8,'karthik jakkula','karthikjakkula840@gmail.com','09063693457','rescue123','rescue','','',50,0,'Active','','2026-05-25 06:30:55'),(9,'M.vinay','vinay@gmail.com','90636 93457','rescue123','rescue','','',50,0,'Active','','2026-05-25 06:32:03'),(10,'M.vikram','vikram@gmail.com','90636 93457','rescue123','rescue','','',50,0,'Active','','2026-05-25 06:33:15'),(11,'preethi','rachelboyajula7@gmail.com','6300104515','rescue123','rescue','','',50,0,'Active','','2026-05-26 04:15:16'),(12,'Hyderabad Blue Cross','Bluecross@gmail.com','08886676074','user123','ngo','Door No 40-3-9, Beside Tabula Rasa, Near Neerus Emporium Showroom, Road No 35, Jubilee Hills, Hyderabad-500033, Telangana','1779776520_editor_639af7aa9c605-cupa-bangalore.png',100,50,'Active','','2026-05-26 06:22:00'),(13,'Rachel','rachel@gmail.com','9346437270','rachel1223','user','','',50,0,'Active','','2026-05-26 07:16:25'),(14,'srinath','srinath@gmail.com','8465975285','srinath123','user','','',50,0,'Active','','2026-05-26 09:21:11');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-26 15:48:29
