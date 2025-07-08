// Jenkinsfile - pipeline build
pipeline {
    agent any
    
    // Step 1. Triggers
    // Are other triggers needed?
    triggers {
        // Poll SCM every x minutes for changes
        // pollSCM('H/x * * * *')
        // Use webhook triggers - does the below work?
        githubPush()
    }
    
    environment {
        PYTHONPATH = "${WORKSPACE}"
        COVERAGE_MIN = '60'
    }
    // Step 2. Environments
    stages {
        stage('Initialization') {
            steps {
                echo 'Building.. Grabbing SCM'
                checkout scm
                
                // Display build information
                script {
                    echo "Build Number: ${env.BUILD_NUMBER}"
                    echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
                    echo "Workspace: ${env.WORKSPACE}"
                }
            }
        }
        
        // 2. ENVIRONMENT SETUP - Install dependencies
        stage('Setup Environment') {
            steps {
                echo 'Building.. setting up Python environment'
                
                // Create virtual environment and install dependencies
                bat '''
                    if exist "venv" rmdir /s /q venv
                    python -m venv venv
                    
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                    pip install flake8 black coverage pytest pytest-cov
                    pip list
                '''
            }
        }
        
        // 3. Code quality checks
        stage('Code Quality') {
            steps {
                echo 'Code Quality - Linting'
                
                bat '''
                    call venv\\Scripts\\activate.bat
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --output-file=flake8-report.txt
                    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --output-file=flake8-full-report.txt
                    
                    RESULTS
                    type flake8-report.txt
                    type flake8-full-report.txt
                '''
                
                // Archive linting reports
                archiveArtifacts artifacts: 'flake8-*.txt', allowEmptyArchive: true
                
                // Erros and Warning
                recordIssues(
                    enabledForFailure: true,
                    aggregatingResults: true,
                    tools: [flake8(pattern: 'flake8-full-report.txt')]
                )
            }
        }
        
        // 3. CODE QUALITY CHECKS - Code formatting
        stage('Code Quality - Formatting') {
            steps {
                echo 'Code Quality.. Format.'
                
                script {
                    def formatResult = bat(
                        script: '''
                            call venv\\Scripts\\activate.bat
                            black --check --diff --color . > black-report.txt 2>&1
                            exit /b %ERRORLEVEL%
                        ''',
                        returnStatus: true
                    )
                    
                    // Archive formatting report
                    archiveArtifacts artifacts: 'black-report.txt', allowEmptyArchive: true
                    
                    if (formatResult != 0) {
                        bat 'type black-report.txt'
                        error("Code formatting check failed. Run 'black .' to fix formatting issues.")
                    } else {
                        echo "Code formatting check passed"
                    }
                }
            }
        }
        
        // 4. TESTING - Run unit tests with coverage
        stage('Testing') {
            steps {
                echo 'Running unit tests with coverage...'
                
                bat '''
                    call venv\\Scripts\\activate.bat
                    
                    REM Run tests with coverage
                    coverage run -m pytest test_app.py -v --tb=short --junitxml=test-results.xml
                    
                    REM Generate coverage reports
                    coverage report --fail-under=%COVERAGE_MIN%
                    coverage html --directory=htmlcov
                    coverage xml --output=coverage.xml
                    
                    REM Display coverage summary
                    coverage report
                '''
            }
            
            post {
                always {
                    // Publish test results
                    publishTestResults(
                        testResultsPattern: 'test-results.xml',
                        mergeResults: true,
                        failureOnError: true
                    )
                    
                    // Publish coverage reports
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report',
                        reportTitles: 'Test Coverage'
                    ])
                    
                    // Archive test artifacts
                    archiveArtifacts artifacts: 'test-results.xml,coverage.xml,htmlcov/**/*', allowEmptyArchive: true
                }
            }
        }
        
        // 5. BUILD PROCESS - Build and verify application
        stage('Build Application') {
            steps {
                echo 'Building Flask application...'
                
                bat '''
                    call venv\\Scripts\\activate.bat
                    
                    REM Test application imports
                    python -c "from app import app; print('Flask app imports successfully')"
                    
                    REM Test database initialization
                    python -c "from app import init_db; init_db(); print('Database initializes successfully')"
                    
                    REM Create build info file
                    echo Build Number: %BUILD_NUMBER% > build-info.txt
                    echo Build Date: %DATE% %TIME% >> build-info.txt
                    echo Branch: %BRANCH_NAME% >> build-info.txt
                    
                    REM List project files
                    dir /b > project-files.txt
                '''
            }
        }
        
        // 5. BUILD PROCESS - Verify build artifacts
        stage('Verify Build Artifacts') {
            steps {
                echo 'Verifying build artifacts...'
                
                bat '''
                    call venv\\Scripts\\activate.bat
                    
                    REM Check required files exist
                    if not exist "app.py" (
                        echo app.py not found
                        exit /b 1
                    )
                    
                    if not exist "requirements.txt" (
                        echo  requirements.txt not found
                        exit /b 1
                    )
                    
                    if not exist "templates" (
                        echo  templates directory not found
                        exit /b 1
                    )
                    
                    echo All required files present
                    echo Build completed successfully
                    
                    REM Display build info
                    type build-info.txt
                '''
                
                // Archive build artifacts
                archiveArtifacts artifacts: 'build-info.txt,project-files.txt', allowEmptyArchive: true
            }
        }
    }
    
    // Post-build actions
    post {
        always {
            echo '🧹 Cleaning up...'
            
            // Clean up virtual environment
            bat '''
                if exist "venv" rmdir /s /q venv
            '''
        }
        
        success {
            echo '🎉 Pipeline completed successfully!'
            
            // Send success notification (optional)
            emailext(
                subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    Build completed successfully!
                    
                    Job: ${env.JOB_NAME}
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                    
                    All tests passed and code quality checks succeeded.
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'your-email@example.com'}"
            )
        }
        
        failure {
            echo 'Pipeline failed!'
            
            // Send failure notification (optional)
            emailext(
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    Build failed!
                    
                    Job: ${env.JOB_NAME}
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                    
                    Please check the build logs for details.
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL ?: 'your-email@example.com'}"
            )
        }
        
        unstable {
            echo 'Build is unstable!'
        }
    }
}