USE BlogService;

-- Create Tables

CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    UserName VARCHAR(255) UNIQUE,
    Password VARCHAR(255),
    Salt VARCHAR(255)
);

CREATE TABLE UserProfiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    Bio TEXT,
    DOB DATE,
    FOREIGN KEY (UserID) REFERENCES Users(id)
);

CREATE TABLE Blogs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    BlogName VARCHAR(255),
    Description TEXT,
    CreatedDate DATETIME,
    UpdatedDate DATETIME,
    FOREIGN KEY (UserID) REFERENCES Users(id)
);

CREATE TABLE Posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    BlogID INT,
    Title VARCHAR(255),
    Content TEXT,
    PostDate DATETIME,
    UpdatedDate DATETIME,
    Visibility INT CHECK (Visibility >= 1 AND Visibility <= 4),
    FOREIGN KEY (BlogID) REFERENCES Blogs(id)
);

CREATE TABLE Comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    PostID INT,
    UserID INT,
    CommentContent TEXT,
    CommentDate DATETIME,
    UpdatedDate DATETIME,
    FOREIGN KEY (PostID) REFERENCES Posts(id),
    FOREIGN KEY (UserID) REFERENCES Users(id)
);

CREATE TABLE Favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    PostID INT,
    FOREIGN KEY (UserID) REFERENCES Users(id),
    FOREIGN KEY (PostID) REFERENCES Posts(id)
);

CREATE TABLE Friends (
    id INT PRIMARY KEY AUTO_INCREMENT,
    UserID1 INT not NULL, -- Applicant
    UserID2 INT not NULL, -- Persons receiving an application
    IsApproved BOOLEAN not NULL DEFAULT FALSE, -- True when UserID2 allows it
    FOREIGN KEY (UserID1) REFERENCES Users(id),
    FOREIGN KEY (UserID2) REFERENCES Users(id)
);

CREATE TABLE Tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    TagName VARCHAR(50)
);

CREATE TABLE PostTags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    PostID INT,
    TagID INT,
    FOREIGN KEY (PostID) REFERENCES Posts(id),
    FOREIGN KEY (TagID) REFERENCES Tags(id)
);

CREATE TABLE LoginHistory (
     id INT PRIMARY KEY AUTO_INCREMENT,
     UserID INT,
     LoginDateTime DATETIME,
     LoginIPAddress VARCHAR(50),
     FOREIGN KEY (UserID) REFERENCES Users(id)
 );

 CREATE TABLE UserInterests (
     id INT PRIMARY KEY AUTO_INCREMENT,
     UserID INT,
     TagID INT,
     SetDateTime DATETIME,
     FOREIGN KEY (UserID) REFERENCES Users(id),
     FOREIGN KEY (TagID) REFERENCES Tags(id)
 );

 CREATE TABLE Groups (
     id INT PRIMARY KEY AUTO_INCREMENT,
     GroupName VARCHAR(255),
     OwnerID INT,
     CreatedDateTime DATETIME,
     UpdatedDateTime DATETIME,
     FOREIGN KEY (OwnerID) REFERENCES Users(id)
 );

 CREATE TABLE GroupMembers (
     id INT PRIMARY KEY AUTO_INCREMENT,
     GroupID INT,
     UserID INT,
     JoinedDateTime DATETIME,
     FOREIGN KEY (GroupID) REFERENCES Groups(id),
     FOREIGN KEY (UserID) REFERENCES Users(id)
 );

 CREATE TABLE Notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    Body TEXT,
    Link TEXT,
    IsRead BOOLEAN,
    CreatedAt DATETIME,
    FOREIGN KEY (UserID) REFERENCES Users(id)
 );

-- Stored Procedure
DELIMITER //
CREATE PROCEDURE CreateUser(IN p_UserName VARCHAR(255), IN p_Password VARCHAR(255), IN p_Salt VARCHAR(255), OUT p_UserID INT)
BEGIN
    INSERT INTO Users(UserName, Password, Salt) VALUES (p_UserName, p_Password, p_Salt);
    SET p_UserID = LAST_INSERT_ID();
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddLoginHistory(IN p_UserID INT, IN p_LoginIPAddress VARCHAR(50))
BEGIN
    INSERT INTO LoginHistory(UserID, LoginDateTime, LoginIPAddress)
    VALUES (p_UserID, NOW(), p_LoginIPAddress);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CreateBlog(IN p_UserID INT, IN p_BlogName VARCHAR(255), IN p_Description TEXT)
BEGIN
    INSERT INTO Blogs(UserID, BlogName, Description, CreatedDate, UpdatedDate)
    VALUES (p_UserID, p_BlogName, p_Description, NOW(), NOW());
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE UpdateBlog(IN p_UserID INT, IN p_BlogID INT, IN p_BlogName VARCHAR(255), IN p_Description TEXT)
BEGIN
    UPDATE Blogs
    SET BlogName = p_BlogName, Description = p_Description, UpdatedDate = NOW()
    WHERE id = p_BlogID AND UserID = p_UserID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteBlog(IN p_UserID INT, IN p_BlogID INT)
BEGIN
    DELETE FROM Blogs
    WHERE id = p_BlogID AND UserID = p_UserID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CreatePost(IN p_BlogID INT, IN p_Title VARCHAR(255), IN p_Content TEXT, IN p_Visibility INT, OUT p_id INT)
BEGIN
    INSERT INTO Posts (BlogID, Title, Content, PostDate, UpdatedDate, Visibility)
    VALUES (p_BlogID, p_Title, p_Content, NOW(), NOW(), p_Visibility);

    SET p_id = LAST_INSERT_ID();
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE EditPost(IN p_PostID INT, IN p_BlogID INT, IN p_Title VARCHAR(255), IN p_Content TEXT, IN p_Visibility INT)
BEGIN
    UPDATE Posts
    SET Title = p_Title,
        Content = p_Content,
        UpdatedDate = NOW(),
        Visibility = p_Visibility
    WHERE id = p_PostID AND BlogID = p_BlogID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeletePost(IN p_PostID INT, IN p_BlogID INT)
BEGIN
    DELETE FROM Posts WHERE id = p_PostID AND BlogID = p_BlogID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetOrCreateTagForPost(IN p_TagName VARCHAR(255), IN p_PostID INT)
BEGIN
    DECLARE v_TagID INT;
    SELECT id INTO v_TagID FROM Tags WHERE TagName = p_TagName;
    IF v_TagID IS NULL THEN -- not exist
        INSERT INTO Tags (TagName) VALUES (p_TagName);
        SELECT LAST_INSERT_ID() INTO v_TagID;
    END IF;
    INSERT INTO PostTags (PostID, TagID) VALUES (p_PostID, v_TagID);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeletePostTag(IN p_TagName VARCHAR(255), IN p_PostID INT)
BEGIN
    DELETE PT FROM PostTags PT
    JOIN Tags T ON PT.TagID = T.id
    WHERE T.TagName = p_TagName AND PT.PostID = p_PostID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CanViewPost(IN pUserID INT, IN pBlogID INT, OUT pCanViewFriendPost BOOLEAN, OUT pCanViewGroupPost BOOLEAN, OUT pCanViewOwnPost BOOLEAN)
BEGIN
    DECLARE vBlogOwnerID INT;
    DECLARE vIsFriend BOOLEAN DEFAULT FALSE;
    DECLARE vIsInSameGroup BOOLEAN DEFAULT FALSE;

    SELECT UserID INTO vBlogOwnerID FROM Blogs WHERE id = pBlogID;

    IF pUserID = vBlogOwnerID THEN
        SET pCanViewFriendPost = TRUE, pCanViewGroupPost = TRUE, pCanViewOwnPost = TRUE;
    ELSE
        SELECT COUNT(*) INTO vIsFriend FROM Friends WHERE (UserID1 = pUserID AND UserID2 = vBlogOwnerID AND IsApproved = TRUE) OR (UserID1 = vBlogOwnerID AND UserID2 = pUserID AND IsApproved = TRUE);
        SELECT COUNT(*) INTO vIsInSameGroup FROM Groups INNER JOIN GroupMembers ON Groups.id = GroupMembers.GroupID WHERE GroupMembers.UserID = pUserID AND Groups.OwnerID = vBlogOwnerID;

        SET pCanViewFriendPost = vIsFriend > 0, pCanViewGroupPost = vIsInSameGroup > 0, pCanViewOwnPost = FALSE;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE InsertComment(IN article_id INT, IN user_id INT, IN comment_text TEXT)
BEGIN
    INSERT INTO Comments(PostID, UserID, CommentContent, CommentDate, UpdatedDate)
    VALUES (article_id, user_id, comment_text, NOW(), NOW());
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE ApproveFriend(IN user_id INT, IN friend_user_id INT)
BEGIN
    UPDATE Friends 
    SET IsApproved = TRUE 
    WHERE (UserID1 = user_id AND UserID2 = friend_user_id) 
    OR (UserID1 = friend_user_id AND UserID2 = user_id);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteFriend(IN user_id INT, IN friend_user_id INT)
BEGIN
    DELETE FROM Friends 
    WHERE (UserID1 = user_id AND UserID2 = friend_user_id) 
    OR (UserID1 = friend_user_id AND UserID2 = user_id);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteUserInterest(IN p_TagName VARCHAR(50), IN p_UserID INT)
BEGIN
    DELETE UI FROM UserInterests UI
    JOIN Tags T ON UI.TagID = T.id
    WHERE T.TagName = p_TagName AND UI.UserID = p_UserID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddUserInterest(IN p_TagName VARCHAR(50), IN p_UserID INT)
BEGIN
    DECLARE v_TagID INT;
    DECLARE v_InterestCount INT;

    SELECT id INTO v_TagID FROM Tags WHERE TagName = p_TagName;
    IF v_TagID IS NULL THEN -- not exist
        INSERT INTO Tags (TagName) VALUES (p_TagName);
        SELECT LAST_INSERT_ID() INTO v_TagID;
    END IF;
    INSERT INTO UserInterests (UserID, TagID, SetDateTime) VALUES (p_UserID, v_TagID, NOW());
END //
DELIMITER ;

-- Function
DELIMITER //
CREATE FUNCTION IsUserBlogOwner(p_UserID INT, p_BlogID INT) RETURNS BOOLEAN
BEGIN
    DECLARE v_UserID INT;
    SELECT UserID INTO v_UserID FROM Blogs WHERE id = p_BlogID;

    IF v_UserID = p_UserID THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END //
DELIMITER ;

-- Views
CREATE VIEW BlogPostsView (PostID, Title, PostDate, UpdatedDate, Visibility, BlogID, NumberOfComments, NumberOfFavorites) AS
SELECT
    P.id AS PostID,
    P.Title,
    P.PostDate,
    P.UpdatedDate,
    P.Visibility,
    P.BlogID,
    (SELECT COUNT(*) FROM Comments C WHERE C.PostID = P.id) AS NumberOfComments,
    (SELECT COUNT(*) FROM Favorites F WHERE F.PostID = P.id) AS NumberOfFavorites
FROM
    Posts P;

CREATE VIEW PostTagsView (PostID, PostTagsID, TagID, TagName) AS
SELECT
    PT.PostID,
    PT.id AS PostTagsID,
    PT.TagID,
    T.TagName
FROM
    PostTags PT
JOIN
    Tags T on PT.TagID = T.id;

CREATE VIEW PostCommentsView AS
SELECT
    C.PostID,
    C.CommentContent,
    C.CommentDate,
    C.UserID,
    U.UserName
FROM
    Comments AS C
JOIN
    Users AS U ON C.UserID = U.id
ORDER BY
    C.CommentDate DESC;

CREATE VIEW FavoritePostsView AS
SELECT
    F.UserID,
    F.PostID,
    P.id AS Post_id,
    P.BlogID,
    P.Content,
    P.Title AS article_title,
    U.UserName AS user_name
FROM
    Favorites AS F
JOIN
    Posts AS P ON F.PostID = P.id
JOIN
    Users AS U ON F.UserID = U.id;

CREATE VIEW BlogPostsViewLimited AS
SELECT
    BPV.BlogID AS blog_id,
    BPV.PostID AS post_id,
    BPV.Title AS article_title,
    U.UserName AS article_author,
    BPV.UpdatedDate AS article_updatetime
FROM BlogPostsView BPV
JOIN Blogs B ON BPV.BlogID = B.id
JOIN Users U ON B.UserID = U.id
WHERE BPV.Visibility = 1
ORDER BY BPV.UpdatedDate DESC
LIMIT 5;

-- trigger
DELIMITER //

CREATE TRIGGER Comments_After_Insert
AFTER INSERT ON Comments
FOR EACH ROW
BEGIN
   DECLARE blogUserID INT;
   DECLARE blogName VARCHAR(255);
   DECLARE postID INT;
   DECLARE blogID INT;

   SELECT B.UserID, B.BlogName, P.id, B.id INTO blogUserID, blogName, postID, blogID
   FROM Posts P
   JOIN Blogs B ON P.BlogID = B.id
   WHERE P.id = NEW.PostID;

   INSERT INTO Notifications (UserID, Body, Link, IsRead, CreatedAt)
   VALUES (blogUserID, CONCAT('Your blog ', blogName, ' has a new comment.'), CONCAT('/view/article/', blogID, '/', postID), FALSE, NOW());
END //

DELIMITER ;

-- data
INSERT INTO Users (UserName, Password, Salt)
VALUES
('teat_a', 'YjFkOWFlZDN0ZXN0YQ==', 'b1d9aed3'), -- cannot login
('test_b', 'YzQ2MjcyY2F0ZXN0Yg==', 'c46272ca'),
('test_c', 'YzE3MGQ0Nzl0ZXN0Yw==', 'c170d479'),
('test_d', 'YmJjNDI0ZjB0ZXN0ZA==', 'bbc424f0'),
('test_e', 'NjEzMzI3OGN0ZXN0ZQ==', '6133278c');

INSERT INTO Blogs (UserID, BlogName, Description, CreatedDate, UpdatedDate)
VALUES
(1, 'Blog1', 'This is Blog1', NOW(), NOW()),
(2, 'Blog2', 'This is Blog2', NOW(), NOW()),
(3, 'Blog3', 'This is Blog3', NOW(), NOW()),
(4, 'Blog4', 'This is Blog4', NOW(), NOW()),
(5, 'Blog5', 'This is Blog5', NOW(), NOW()),
(1, 'Blog6', 'This is Blog6', NOW(), NOW()),
(2, 'Blog7', 'This is Blog7', NOW(), NOW()),
(3, 'Blog8', 'This is Blog8', NOW(), NOW()),
(4, 'Blog9', 'This is Blog9', NOW(), NOW()),
(5, 'Blog10', 'This is Blog10', NOW(), NOW());

INSERT INTO Posts (BlogID, Title, Content, PostDate, UpdatedDate, Visibility)
VALUES
(1, 'Title1', 'This is Content1', NOW(), NOW(), 1),
(2, 'Title2', 'This is Content2', NOW(), NOW(), 2),
(3, 'Title3', 'This is Content3', NOW(), NOW(), 3),
(4, 'Title4', 'This is Content4', NOW(), NOW(), 4),
(5, 'Title5', 'This is Content5', NOW(), NOW(), 1),
(6, 'Title6', 'This is Content6', NOW(), NOW(), 2),
(7, 'Title7', 'This is Content7', NOW(), NOW(), 3),
(8, 'Title8', 'This is Content8', NOW(), NOW(), 4),
(9, 'Title9', 'This is Content9', NOW(), NOW(), 1),
(10, 'Title10', 'This is Content10', NOW(), NOW(), 2);

INSERT INTO Comments (PostID, UserID, CommentContent, CommentDate, UpdatedDate)
VALUES
(1, 1, 'This is Comment1', NOW(), NOW()),
(2, 2, 'This is Comment2', NOW(), NOW()),
(3, 3, 'This is Comment3', NOW(), NOW()),
(4, 4, 'This is Comment4', NOW(), NOW()),
(5, 5, 'This is Comment5', NOW(), NOW()),
(6, 1, 'This is Comment6', NOW(), NOW()),
(7, 2, 'This is Comment7', NOW(), NOW()),
(8, 3, 'This is Comment8', NOW(), NOW()),
(9, 4, 'This is Comment9', NOW(), NOW()),
(10, 5, 'This is Comment10', NOW(), NOW());

INSERT INTO Groups (GroupName, OwnerID, CreatedDateTime, UpdatedDateTime)
VALUES
('Group1', 1, NOW(), NOW()),
('Group2', 2, NOW(), NOW()),
('Group3', 3, NOW(), NOW());

INSERT INTO GroupMembers (GroupID, UserID, JoinedDateTime)
VALUES
(1, 1, NOW()),
(1, 2, NOW()),
(1, 3, NOW()),
(1, 4, NOW()),
(1, 5, NOW()),
(2, 1, NOW()),
(2, 2, NOW()),
(2, 3, NOW()),
(3, 4, NOW()),
(3, 5, NOW());

