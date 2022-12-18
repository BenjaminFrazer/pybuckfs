
# Table of Contents

1.  [Overview](#org71222d4)
2.  [Schema](#org587c9ce)
    1.  [File UUID](#org13a7165)
    2.  [Tracked Directories](#org52de727)
    3.  [Buckets](#orgd8179ce)
    4.  [Remotes](#orgcee25c9)
    5.  [Tags](#org295555f)
        1.  [Reserved tags](#orge51c6b6)
        2.  [Acceptable characters](#orgd7f44fc)
    6.  [File Deletion](#org41bd44c)
    7.  [File renaming](#orgdd303bf)
    8.  [Manual resync](#orgcf2ee3c)
3.  [Philosophy](#org5be18c9)
4.  [Caching](#orga9d207e)
    1.  [Cache Schema](#org81fd9f0)
    2.  [Syncing](#orgf65783a)
5.  [Migrating](#org506116c)
6.  [Project Features](#org5e5019a)
7.  [Project timeline](#orgdd56bbf)



<a id="org71222d4"></a>

# Overview

⚠ This project is as yet not fully implemented.

Buckfs aims to implement a file management system to work with files in a hierarchy agnostic fashion. Core to the buckfs philosophy is the definition of a simple and completely flexible schema which can be easily tailored to the user&rsquo;s needs.

Features include:

-   Simple, transparent, OS agnostic schema
-   Simple CLI for operations such as:
    -   **`buckfs sync`:** to sync the present working directory and all it&rsquo;s children
    -   **`buckfs sync <filename>`:** to sync just one file
-   Object based file synchronisation
-   Git like ignore file matching
-   File hierarchy agnostic synchronisation
-   Simple file tagging syntax
-   Optional simlink based file hierarchy

Where is buckfs suitable:

-   You have large numbers of files you want to flexibly interact with and keep synchronised across computer systems.

Where is buckfs not suitable:

-   Where you have lots of predominantly very small files you wish to track. This is because each individual file includes at least ~10 bytes of metadata which is stored in and synchronised with the main files. Where average file sizes are very small, this can start to become a major component of storage.


<a id="org587c9ce"></a>

# Schema


<a id="org13a7165"></a>

## File UUID

The core distinguishing feature of buckfs is to uniquely identify files not by their file path, rather using a unique universal identifier (UUID) which is inserted into the file name using the following syntax:

    <filename>[<UUID].<extention>

Some example filenames might be:

-   `my expenditures[abuY06Ed9].csv`
-   `haiku about trees[S4uY07Ed9].txt`


<a id="org52de727"></a>

## Tracked Directories

-   A tracked directory in buckfs parlance is simply a file describing a structuring of tracked files.
-   In buckfs this is done by simply adding the directory using the `buckfs add <dir name>` command. This does the following things:
    -   Inserts a new UUID into the directory name.
    -   Creates a hidden file in the root of this directory using the following naming syntax `.<dir name>[<uuid>]`.
    -   Populates this file with the directory structure
-   Directories can be tracked by marking the directory with a UUID in the same syntax as a file.
-   buckfs will then create a file that describes the structure of this directory
-   You can `pull` any tracked repositories by UUID which will create a local version of that directory and it&rsquo;s children in the target directory.


<a id="orgd8179ce"></a>

## Buckets

-   A bucket simply describes an unstructured set of tracked files/objects that buckfs operates on. Buckets can exist on both cloud or local storage.
-   Each local bucket must be declared in the `.buckfsrc` file.


<a id="orgcee25c9"></a>

## Remotes

-   A remote is simply another bucket that is defined as a synchronization target (remote copy) of the current bucket being worked on.


<a id="org295555f"></a>

## Tags

-   Tags are optional keyword value pair that are associated with a particular file by it&rsquo;s UUID
-   Tags are defined on a bucket by bucket basis under the `.buckfstags` file which is usually in the root of the bucket. This is can be configured on a bucket by bucket basis in the `buckfs.yaml`.
-   Every file which has tags, has a shadow tags file in the tags directory which contains a newline separated list of all it&rsquo;s tags.
-   Each new tag is associated with a new file using the syntax: `<file name>[<uuid of asociated file>].buckfstag`
-   When a file is tagged, it&rsquo;s uuid is placed in the corresponding tags file
-   Since the tags file has it&rsquo;s own uuid, it can be kept in synchronism with the remote in the same way as any other file in buckfs

-   Choosing between a single file per tag containing UUIDs vs a single file per file containing associated tags is a tough choice
-   features of single file per tag
    -   A single file per tag is quicker to parse and query when selecting files by tag, which is the common use case.
    -   this also means that tags files can be treated no differently to any other file types using a UUID in the heading
    -   It also uses less storage space and allows tags to be easily renamed and copied from another.
    -   Less intuitive
    -   less storage space
    -   quicker to query for files matching a tag
    -   Deletions/renaming on different file systems cannot easily be merged
-   features of shadow file
    -   This cant be done when using a shadow file since the shadow file must include the UUID the file it is associated with
    -   this means that the tags directory must be explicitly ignored and tags files only fetched when a given object is synced.
    -   A shadow tags file per file however is much more intuitive to manually edit and allows for partial synchronisation of tags
    -   additional logic during sync to search for implicit tags files that should be synced
    -   Additional logic during sync to find both the file itself and it&rsquo;s associated tags file, first syncing the tags file then the file it&rsquo;s self.
    -   This nicely encodes propagation of a deletion (for example the file is deleted on the remote by another client):
        -   Though the file is deleted on the remote, It&rsquo;s shadow file will remain including the `_deleted` tag.
        -   If a file has been modified then the tags file always also be modified. This is because every modification to the file will update the `_tmodified` tag.
        -   If the server version is more recent then it wins and the local shadow file will be taken which includes the deletion tag
        -   The shadow file is synchronised first thus if the server version is newer than the
    -   slower to build database (more individual files to parse)
    -   Can easily resolve separate deletions


<a id="orge51c6b6"></a>

### Reserved tags

Tags are also used for internal buckfs housekeeping and are as such reserved. All reserved tags are prefixed with and `-`. These include:

-   **\_deleted=<>:** This file has been marked for deletion on the remote.
-   **\_renamed=<new name>:** This file has been marked for renaming on the remote.
-   **\_remote<sub>t</sub><sub>modified</sub>:** The most recent modification time of all remote versions at the time of last synchronisation.
    -   This informs whether the md5 must be requested.


<a id="orgd7f44fc"></a>

### Acceptable characters

The main constraint to tags is that they must of course work within a filename, since the name of a tag is defined by the name of a tags file. Further more, though not an explicit requirement


<a id="org41bd44c"></a>

## File Deletion

-   Buckfs will almost never delete a file from the remote. When you delete a local copy of a file this is simply treated as a change in structure to a directory to no-longer include this file, however the file will persist on the remote and be available within all other directories that reference it.
-   Full file deletion in buckfs is a specific operation which must be invoked by the user explicitly using the `buckfs delete <file>` command.


<a id="orgdd303bf"></a>

## File renaming

The default behaviour, as long as the UUID remains valid, is that renamed files will not change on the remote or in other directories where it is present. Renaming on the remote must be specifically invoked using the `buckfs rename <file> <new name>` command. Internally this simply tags the file as renamed with the


<a id="orgcf2ee3c"></a>

## Manual resync

Buckfs implicitly assumes that all changes made to internal files such as directory or tag files are done using the buckfs CLI. This means that the cache is also kept up-to-date. If however change is made manually, for example manually adding a uuid to a tags file, then the database will have to be manually synced to accept this change. `buckfs sync <file>` can be run on any internal file such as a tags file and will update the cache.

If the cache ends up corrupted, the entire database may be rebuilt using the `-a` flag. This will delete the cache and then walk the local bucket file hierarchy rebuilding the local cache including tag files.


<a id="org5be18c9"></a>

# Philosophy

This solves many of the core problems I have with file management systems such as:

-   Problems arising from rearranging your file system - due to the difficulty distinguishing file moves from file deletion and edits.
-   OS lockin - Particular cloud services provide their own synchronisation tools, but support on different OS&rsquo;s is varied e.g. google chrome.
-   Vendor lock in - the maintainers of your critical tools cease support or make it difficult to transition away from their tools once you are invested. **A:** buckfs is at it&rsquo;s core just the definition of a simple schema. This schema could in theory be easily implemented in any language for any os and with any cloud provider. Further more, the  code is open-source and can thus be freely copied and modified and redistributed
-   Database corruption - Some file management systems rely heavily on databases which, if they fail or become corrupted in some way can be challenging to fix especially for the novice. **A:** Though buckfs makes use of databases, this is purely for the purpose off caching information for that is either implicitly tied to the files (UUID, time modified) or stored in human readable text files in `.buckfs` directories. Thus all buckfs tools can be used without a database, and  the database can be easily reconstructed.
-   Inefficient sync with file renaming - Frequently renaming and or moving a file will cause redundant copies to occur during synchronisation. **A:** on buckfs you can change/move the file without limits and, as long as the UUID does not change, this will still be treated as the same object and no redundant copies will occur.
-   Granular synchronisation - Frequently you only wish to sync changes on a small subset of files which you have been editing. **A:** Invoke the `buckfs sync` in the directory you wish to sync, and only the tracked files in this and child directory will be synchronised with the remote(s).
-   Inadvertent deletion - Sometimes things happen on your local file system that you don&rsquo;t wish to propagate to your server version. **A:** on buckfs files must be explicitly deleted using the `buckfs delete =<file|directory>` command for the file to be deleted on the remote on the next sync. Deletions of tracked files is simply seen as a change to the directory structure.
-   Over synchronisation - Most synchronisation systems do synchronisation on a directory which means you often end up syncing files you don&rsquo;t want to such as temp files, log files, notes etc. **A:** Buckfs will only synchronise the files that contain a UUID
-   File hierarchy lock-in - When you structure your files in a particular way and then find it difficult to change. **A:** Pull a simlink version of your directory, rename, do your rearranging, and resync. In buckfs directories are just files that store a structuring of objects based on their IDs. Thus syncing a restructured directory separately is extremely cheap, and changes to objects in either will be persisted to both versions.
-   Filing ambiguity - This file belongs in both `/haikus` and `/trees`! How will i remember where I put it? **A:** Put it in both using tags.


<a id="orga9d207e"></a>

# Caching

In order to minimise sync times buckfs creates a local cache of each bucket using an sqlite database. These are typically named according to the following schema: `~/config/buckfs/<bucket name>_cache.db`

The cache allows each file selected for synchronisation


<a id="org81fd9f0"></a>

## Cache Schema

The data stored in the cache includes the following fields for each file:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">UUID</th>
<th scope="col" class="org-left">md5</th>
<th scope="col" class="org-left">tmodified</th>
<th scope="col" class="org-left">path</th>
<th scope="col" class="org-left">isdir</th>
<th scope="col" class="org-left">isfile</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">&#x2026;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
<td class="org-left">&#xa0;</td>
</tr>
</tbody>
</table>

Where:

-   **md5:** is the md5 hash of the file content since last synchronisation
-   **tmodified:** The time of the most recent modification since the last sync (this can be quicker than checking the hash)
-   **tsynced:** Time that the object is successfully synchronized with the remote.


<a id="orgf65783a"></a>

## Syncing

-   Sync is  called either on a single file, or collection of files
-   We first figure out common information such as:
    -   The bucket that the files are associated with
-   We implicitly add all of the tag files to the sync list
-   If there isn&rsquo;t a daemon running, we must then validate the cache
    -   We extract basic information about the files in question such as:
        -   UUID
        -   Size
        -   Last time modified
        -   what the closest tracked parent directory is (what dir the file belongs to)
    -   We check the bucket
-   we then order these files with the implicit files first, followed by the smallest to the largest files.
-   these are first looked up in the cache by their UUID.
-   We


<a id="org506116c"></a>

# Migrating


<a id="org5e5019a"></a>

# Project Features

-   Single client CLI Application to sync files with UUID with a server
    -   configuration
        -   Configuration options are stored in the `.buckfs` file.
        -   the s3 bucket name
        -   the access credentials (IAM user)
    -   single sync command with no arguments run in directory will synchronise that directory with the server
-   Support multiple AWS credentials and S3 buckets
    -   Optionally the AWS credentials and S3 bucket information may be specified in a hidden `.buckfs` folder in the root directory which is being kept in sync.
    -   If no such dot directory is found then the default configuration bucket and credentials are used
-   CLI to manage local files
    -   Track and untrack files (i.e. add uuid)
-   daemon to regularly rebuild and synchronise files


<a id="orgdd56bbf"></a>

# Project timeline

