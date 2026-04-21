@echo off
REM ============================================================
REM  Run Spark Analytics for Personal Expense Tracker
REM  Make sure SPARK_HOME and JAVA_HOME are set
REM ============================================================

echo.
echo ============================================================
echo   Expense Tracker - Spark Analytics Runner
echo ============================================================
echo.

REM Check if SPARK_HOME is set
if "%SPARK_HOME%"=="" (
    echo ERROR: SPARK_HOME is not set.
    echo Please set SPARK_HOME to your Spark installation directory.
    echo Example: set SPARK_HOME=C:\spark
    pause
    exit /b 1
)

REM Check if JAVA_HOME is set
if "%JAVA_HOME%"=="" (
    echo ERROR: JAVA_HOME is not set.
    echo Please set JAVA_HOME to your JDK installation directory.
    pause
    exit /b 1
)

echo   SPARK_HOME = %SPARK_HOME%
echo   JAVA_HOME  = %JAVA_HOME%
echo.

REM Find MySQL JDBC connector JAR
set JDBC_JAR=
for %%f in ("%SPARK_HOME%\jars\mysql-connector-*.jar") do set JDBC_JAR=%%f

if "%JDBC_JAR%"=="" (
    echo WARNING: MySQL JDBC connector not found in %SPARK_HOME%\jars\
    echo Looking in current directory...
    for %%f in ("mysql-connector-*.jar") do set JDBC_JAR=%%f
)

if "%JDBC_JAR%"=="" (
    echo ERROR: MySQL JDBC connector JAR not found!
    echo Download from: https://dev.mysql.com/downloads/connector/j/
    echo Place the JAR in: %SPARK_HOME%\jars\
    pause
    exit /b 1
)

echo   JDBC JAR   = %JDBC_JAR%
echo.
echo   Starting Spark job...
echo.

REM Run the Spark analytics script
%SPARK_HOME%\bin\spark-submit --jars "%JDBC_JAR%" "%~dp0spark_analytics.py"

echo.
echo ============================================================
echo   Spark job finished. Check results in phpMyAdmin.
echo ============================================================
echo.
pause
