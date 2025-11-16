DEFAULT_QUERIES = [
    # Typos vs correct (definition + example)
    {"id": "q1_correct", "text": "Explain what a relational database is and give a short example.", "tag": "typo_test", "typo": False},
    {"id": "q1_typo", "text": "Exlain what a relational databse is and give a short exmple.", "tag": "typo_test", "typo": True},

    # Context preservation: question + follow-up that assumes previous answer
    {"id": "q2_1", "text": "What is database normalization and why is it used?", "tag": "context_test", "typo": False},
    {"id": "q2_2", "text": "How does Third Normal Form (3NF) differ from Boyce-Codd Normal Form (BCNF)?", "tag": "context_test_followup", "typo": False},

    # Ambiguous short query that benefits from context
    {"id": "q3_ambig", "text": "What is a transaction?", "tag": "ambig_test", "typo": False},
    {"id": "q3_clarify", "text": "In databases, explain ACID transactions briefly.", "tag": "ambig_followup", "typo": False},

    # Long / noisy query vs cleaned version
    {"id": "q4_clean", "text": "In a distributed database system, how does replication affect consistency and availability? Provide trade-offs and an example.", "tag": "long_test", "typo": False},
    {"id": "q4_noisy", "text": "So I heard about replication and stuff — like in distributed systems, how does replication affect consistency AND availability, and can you give a real world example? I'm trying to understand trade-offs.", "tag": "long_test_noisy", "typo": False},

    # Numeric/statistics question with typo
    {"id": "q5_correct", "text": "How do query optimizers estimate the number of distinct values for an attribute?", "tag": "numeric_test", "typo": False},
    {"id": "q5_typo", "text": "How do query optimizers estmate the numbr of distinct vales for an attribute?", "tag": "numeric_test", "typo": True},

    # Exact-phrase request
    {"id": "q6_correct", "text": "Define the ACID properties of transactions with a short example for each.", "tag": "exact_test", "typo": False},
    {"id": "q6_typo", "text": "Defne the ACID proprties of transactions with a short exmple for each.", "tag": "exact_test", "typo": True}
]

ADDITIONAL_QUERIES = [
    # Data integrity concept
    {"id": "q7_correct", "text": "What is the difference between a primary key and a foreign key in a relational database?", "tag": "typo_test", "typo": False},
    {"id": "q7_typo", "text": "Wat is teh diffrnce btween a primry ky and a forign kye in a relashonal databse?", "tag": "typo_test", "typo": True},

    # SQL joins
    {"id": "q8_correct", "text": "Explain the difference between INNER JOIN and LEFT JOIN in SQL with examples.", "tag": "typo_test", "typo": False},
    {"id": "q8_typo", "text": "Explan teh diffrence btwen INER JOIN an LEFT JOON in SQL wth exampels.", "tag": "typo_test", "typo": True},

    # Indexing
    {"id": "q9_correct", "text": "How does creating an index improve query performance in a database?", "tag": "typo_test", "typo": False},
    {"id": "q9_typo", "text": "Hw dos creatng an indx imprve qurey performnce in databse?", "tag": "typo_test", "typo": True},

    # Transactions and rollback
    {"id": "q10_correct", "text": "What happens when a database transaction fails and needs to be rolled back?", "tag": "typo_test", "typo": False},
    {"id": "q10_typo", "text": "Wat hapens wen a databse trnsacton fals nd neds to be rolld back?", "tag": "typo_test", "typo": True},

    # Normalization purpose
    {"id": "q11_correct", "text": "Why is normalization important in database design?", "tag": "typo_test", "typo": False},
    {"id": "q11_typo", "text": "Wy is normlizaton imporant in databse dezign?", "tag": "typo_test", "typo": True}
]

MORE_QUERIES = [

    # 1 – Transactions
    {"id": "q1_correct", "text": "What happens during a database transaction commit?", "tag": "typo_test", "typo": False},
    {"id": "q1_typo", "text": "Wat hapens durring a databse transacton commt?", "tag": "typo_test", "typo": True},

    # 2 – Indexing
    {"id": "q2_correct", "text": "How does a B+ tree improve indexing performance?", "tag": "typo_test", "typo": False},
    {"id": "q2_typo", "text": "How doez a B+ tre improe indxng perfomance?", "tag": "typo_test", "typo": True},

    # 3 – Normalization
    {"id": "q3_correct", "text": "Explain the purpose of database normalization.", "tag": "typo_test", "typo": False},
    {"id": "q3_typo", "text": "Exlain the prpose of databse normaliztion.", "tag": "typo_test", "typo": True},

    # 4 – ACID properties
    {"id": "q4_correct", "text": "What are the ACID properties of a transaction?", "tag": "typo_test", "typo": False},
    {"id": "q4_typo", "text": "Wat are the ACID propertes of a transction?", "tag": "typo_test", "typo": True},

    # 5 – Deadlocks
    {"id": "q5_correct", "text": "What conditions lead to a deadlock in concurrency control?", "tag": "typo_test", "typo": False},
    {"id": "q5_typo", "text": "Wat conditons led to a deadlok in concurency contrl?", "tag": "typo_test", "typo": True},

    # 6 – Foreign keys
    {"id": "q6_correct", "text": "Why are foreign keys important in relational schemas?", "tag": "typo_test", "typo": False},
    {"id": "q6_typo", "text": "Why are forign kys importnt in relatonal schems?", "tag": "typo_test", "typo": True},

    # 7 – Isolation levels
    {"id": "q7_correct", "text": "What is the difference between read committed and repeatable read isolation?", "tag": "typo_test", "typo": False},
    {"id": "q7_typo", "text": "Wha is the diffrence betwen read commited and reepatable read isolaton?", "tag": "typo_test", "typo": True},

    # 8 – Query optimization
    {"id": "q8_correct", "text": "How does the query optimizer choose efficient execution plans?", "tag": "typo_test", "typo": False},
    {"id": "q8_typo", "text": "How doz the query optimzer chooe efcient executon plans?", "tag": "typo_test", "typo": True},

    # 9 – Locking
    {"id": "q9_correct", "text": "Explain the difference between shared locks and exclusive locks.", "tag": "typo_test", "typo": False},
    {"id": "q9_typo", "text": "Exlain the diffrnce betwen shared loks and excluive loks.", "tag": "typo_test", "typo": True},

    # 10 – Write-ahead logging
    {"id": "q10_correct", "text": "What is the purpose of write-ahead logging in databases?", "tag": "typo_test", "typo": False},
    {"id": "q10_typo", "text": "What is the prpose of wite-ahead loging in databse?", "tag": "typo_test", "typo": True},

    # 11 – Hash indexing
    {"id": "q11_correct", "text": "When is hash indexing preferred over tree-based indexing?", "tag": "typo_test", "typo": False},
    {"id": "q11_typo", "text": "Wen is hash indxng prefered ovr tree-based indxng?", "tag": "typo_test", "typo": True},

    # 12 – Joins
    {"id": "q12_correct", "text": "What is the difference between an inner join and an outer join?", "tag": "typo_test", "typo": False},
    {"id": "q12_typo", "text": "Wat is the diffrence btwen an iner jon and an outer jon?", "tag": "typo_test", "typo": True},

    # 13 – Query execution
    {"id": "q13_correct", "text": "Describe how a SQL query is processed by the execution engine.", "tag": "typo_test", "typo": False},
    {"id": "q13_typo", "text": "Descrbe how a SQL qury is procesed by the executon engin.", "tag": "typo_test", "typo": True},

    # 14 – Recovery
    {"id": "q14_correct", "text": "How does a database restore state after a system crash?", "tag": "typo_test", "typo": False},
    {"id": "q14_typo", "text": "How doz a datbase restre stae afer a systm crash?", "tag": "typo_test", "typo": True},

    # 15 – Functional dependencies
    {"id": "q15_correct", "text": "What role do functional dependencies play in normalization?", "tag": "typo_test", "typo": False},
    {"id": "q15_typo", "text": "Wat role do functonal dependnces ply in normalizaton?", "tag": "typo_test", "typo": True},

    # 16 – Serializability
    {"id": "q16_correct", "text": "Explain the concept of conflict serializability.", "tag": "typo_test", "typo": False},
    {"id": "q16_typo", "text": "Exlain the conecpt of conflct seralizablity.", "tag": "typo_test", "typo": True},

    # 17 – Logging
    {"id": "q17_correct", "text": "Why is log truncation necessary during database recovery?", "tag": "typo_test", "typo": False},
    {"id": "q17_typo", "text": "Why is log trunation necesary dring databse recovry?", "tag": "typo_test", "typo": True},

    # 18 – Buffer pool
    {"id": "q18_correct", "text": "How does the buffer pool improve database performance?", "tag": "typo_test", "typo": False},
    {"id": "q18_typo", "text": "How doz the bufer pol improe databse perfomance?", "tag": "typo_test", "typo": True},

    # 19 – Two-phase locking
    {"id": "q19_correct", "text": "What is the purpose of two-phase locking in concurrency control?", "tag": "typo_test", "typo": False},
    {"id": "q19_typo", "text": "Wat is the prpose of two-phse loking in concurency contrl?", "tag": "typo_test", "typo": True},

    # 20 – Query planning
    {"id": "q20_correct", "text": "How does a database choose between different query plans?", "tag": "typo_test", "typo": False},
    {"id": "q20_typo", "text": "How doz a databse chuse betwen diffrent qury plans?", "tag": "typo_test", "typo": True},

    # 21 – Storage models
    {"id": "q21_correct", "text": "Explain the difference between row store and column store databases.", "tag": "typo_test", "typo": False},
    {"id": "q21_typo", "text": "Exlain the difrence betwen row stor and colmn stor databse.", "tag": "typo_test", "typo": True},

    # 22 – Materialized views
    {"id": "q22_correct", "text": "What is a materialized view and why is it useful?", "tag": "typo_test", "typo": False},
    {"id": "q22_typo", "text": "Wat is a materlized vew and why is it usful?", "tag": "typo_test", "typo": True},

    # 23 – Relational algebra
    {"id": "q23_correct", "text": "How do selection and projection differ in relational algebra?", "tag": "typo_test", "typo": False},
    {"id": "q23_typo", "text": "How do selecton and projecton diffr in relatinal algebr?", "tag": "typo_test", "typo": True},

    # 24 – RAID
    {"id": "q24_correct", "text": "What are the advantages of using RAID for storage reliability?", "tag": "typo_test", "typo": False},
    {"id": "q24_typo", "text": "Wat are the advatages of using RAID for storag relabilty?", "tag": "typo_test", "typo": True},

    # 25 – Cost estimation
    {"id": "q25_correct", "text": "How does the cost model estimate the cost of different query plans?", "tag": "typo_test", "typo": False},
    {"id": "q25_typo", "text": "How doz the cost model estmate the cost of diffrent qury plans?", "tag": "typo_test", "typo": True},

    # 26 – Merge join
    {"id": "q26_correct", "text": "When is a merge join more efficient than a nested loop join?", "tag": "typo_test", "typo": False},
    {"id": "q26_typo", "text": "Wen is a merj jon more efcient than a nestd lop jon?", "tag": "typo_test", "typo": True},

    # 27 – Hash join
    {"id": "q27_correct", "text": "How does a hash join process matching tuples?", "tag": "typo_test", "typo": False},
    {"id": "q27_typo", "text": "How doz a hash jon proces matchng tupes?", "tag": "typo_test", "typo": True},

    # 28 – Schema design
    {"id": "q28_correct", "text": "Why is schema design important in relational databases?", "tag": "typo_test", "typo": False},
    {"id": "q28_typo", "text": "Why is schem design importnt in relatonal databse?", "tag": "typo_test", "typo": True},

    # 29 – Durability
    {"id": "q29_correct", "text": "What ensures durability after a crash in a database system?", "tag": "typo_test", "typo": False},
    {"id": "q29_typo", "text": "Wat ensures durablity afer a crash in a databse systm?", "tag": "typo_test", "typo": True},

    # 30 – Execution engine
    {"id": "q30_correct", "text": "How does the execution engine process a SQL query?", "tag": "typo_test", "typo": False},
    {"id": "q30_typo", "text": "How doz the executon engin proces a SQL qury?", "tag": "typo_test", "typo": True},

    # 31 – Page storage
    {"id": "q31_correct", "text": "What is a database page and how is it structured?", "tag": "typo_test", "typo": False},
    {"id": "q31_typo", "text": "Wat is a databse pae and how is it structurd?", "tag": "typo_test", "typo": True},

    # 32 – Query parsing
    {"id": "q32_correct", "text": "What steps occur during SQL query parsing?", "tag": "typo_test", "typo": False},
    {"id": "q32_typo", "text": "Wat stpes ocur dring SQL qury parsng?", "tag": "typo_test", "typo": True},

    # 33 – Heaps vs sorted files
    {"id": "q33_correct", "text": "When is a heap file more efficient than a sorted file?", "tag": "typo_test", "typo": False},
    {"id": "q33_typo", "text": "Wen is a hep file more efcient than a sortd file?", "tag": "typo_test", "typo": True},

    # 34 – Query rewriting
    {"id": "q34_correct", "text": "How does a database perform query rewriting to improve performance?", "tag": "typo_test", "typo": False},
    {"id": "q34_typo", "text": "How doz a databse perfrm qury rewritng to improe perfomance?", "tag": "typo_test", "typo": True},

    # 35 – Bitmap indexes
    {"id": "q35_correct", "text": "What are bitmap indexes and when are they useful?", "tag": "typo_test", "typo": False},
    {"id": "q35_typo", "text": "Wat are bitmp indxex and wen are they usful?", "tag": "typo_test", "typo": True},

    # 36 – Cascading aborts
    {"id": "q36_correct", "text": "What causes cascading aborts in transaction systems?", "tag": "typo_test", "typo": False},
    {"id": "q36_typo", "text": "Wat causes cascadng aborts in transacton systms?", "tag": "typo_test", "typo": True},

    # 37 – ARIES
    {"id": "q37_correct", "text": "Explain how ARIES performs recovery after a crash.", "tag": "typo_test", "typo": False},
    {"id": "q37_typo", "text": "Exlain how ARIES perfrms recovry afer a crash.", "tag": "typo_test", "typo": True},

    # 38 – Concurrency anomalies
    {"id": "q38_correct", "text": "What anomalies does concurrency control aim to prevent?", "tag": "typo_test", "typo": False},
    {"id": "q38_typo", "text": "Wat anomlies doz concurency contrl aim to prvnt?", "tag": "typo_test", "typo": True},

    # 39 – LSM trees
    {"id": "q39_correct", "text": "Why do write-heavy systems often use LSM trees?", "tag": "typo_test", "typo": False},
    {"id": "q39_typo", "text": "Why do writ-hevy systms oftn use LSM tres?", "tag": "typo_test", "typo": True},

    # 40 – Page replacement
    {"id": "q40_correct", "text": "How does a database buffer manager choose pages to evict?", "tag": "typo_test", "typo": False},
    {"id": "q40_typo", "text": "How doz a databse bufer managr chuse pages to evct?", "tag": "typo_test", "typo": True},

    # 41 – Cascaded rollbacks
    {"id": "q41_correct", "text": "What is a cascaded rollback and how is it prevented?", "tag": "typo_test", "typo": False},
    {"id": "q41_typo", "text": "Wat is a cascadad rolback and how is it prevnted?", "tag": "typo_test", "typo": True},

    # 42 – Hierarchical storage
    {"id": "q42_correct", "text": "How do multi-level storage hierarchies improve efficiency?", "tag": "typo_test", "typo": False},
    {"id": "q42_typo", "text": "How do mult-level storag hierarhies improe eficency?", "tag": "typo_test", "typo": True},

    # 43 – Tuple formats
    {"id": "q43_correct", "text": "What information is stored in a tuple header in a row store?", "tag": "typo_test", "typo": False},
    {"id": "q43_typo", "text": "Wat informaton is storred in a tuple heder in a row stor?", "tag": "typo_test", "typo": True},

    # 44 – Execution pipelines
    {"id": "q44_correct", "text": "How do execution pipelines improve query throughput?", "tag": "typo_test", "typo": False},
    {"id": "q44_typo", "text": "How do executon pipelins improe qury throuput?", "tag": "typo_test", "typo": True},

    # 45 – Schema evolution
    {"id": "q45_correct", "text": "Why is schema evolution a challenge in long-lived databases?", "tag": "typo_test", "typo": False},
    {"id": "q45_typo", "text": "Why is schem evoluton a chalenge in long-lved databse?", "tag": "typo_test", "typo": True},

    # 46 – Data independence
    {"id": "q46_correct", "text": "What is logical data independence and why does it matter?", "tag": "typo_test", "typo": False},
    {"id": "q46_typo", "text": "Wat is logicl data independnce and why doz it mater?", "tag": "typo_test", "typo": True},

    # 47 – Query semantics
    {"id": "q47_correct", "text": "Explain the semantics of GROUP BY and HAVING clauses.", "tag": "typo_test", "typo": False},
    {"id": "q47_typo", "text": "Exlain the semantcs of GROUP BY and HAVNG clasess.", "tag": "typo_test", "typo": True},

    # 48 – Cost-based optimization
    {"id": "q48_correct", "text": "How does cost-based optimization improve query execution?", "tag": "typo_test", "typo": False},
    {"id": "q48_typo", "text": "How doz cost-based optimzaton improe qury executon?", "tag": "typo_test", "typo": True},

    # 49 – Write amplification
    {"id": "q49_correct", "text": "What causes write amplification in storage engines?", "tag": "typo_test", "typo": False},
    {"id": "q49_typo", "text": "Wat causes writ amplficaton in storag engins?", "tag": "typo_test", "typo": True},

    # 50 – Query logs
    {"id": "q50_correct", "text": "How are query logs used to analyze user access patterns?", "tag": "typo_test", "typo": False},
    {"id": "q50_typo", "text": "How are qury logs used to analyz usr acces paterns?", "tag": "typo_test", "typo": True},
]
